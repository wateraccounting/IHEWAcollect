# -*- coding: utf-8 -*-
# General modules
import os
import sys
import shutil

import datetime

import requests
from requests.auth import HTTPBasicAuth

import numpy as np
import pandas as pd

# import h5py
from netCDF4 import Dataset

# IHEWAcollect Modules
try:
    from ..collect import \
        Extract_Data_gz, Open_tiff_array, Save_as_tiff
    from ..gis import GIS
    from ..dtime import Dtime
    from ..util import Log
except ImportError:
    from IHEWAcollect.templates.collect import \
        Extract_Data_gz, Open_tiff_array, Save_as_tiff
    from IHEWAcollect.templates.gis import GIS
    from IHEWAcollect.templates.dtime import Dtime
    from IHEWAcollect.templates.util import Log


__this = sys.modules[__name__]


def _init(status, conf):
    # From download.py
    __this.status = status
    __this.conf = conf

    # Init supported classes
    __this.GIS = GIS(status, conf)
    __this.Dtime = Dtime(status, conf)
    __this.Log = Log(conf['log'])

    # For download
    __this.username = conf['account']['data']['username']
    __this.password = conf['account']['data']['password']
    __this.apitoken = conf['account']['data']['apitoken']


def DownloadData(status, conf) -> int:
    """
    This scripts downloads ASCAT SWI data from the VITO server.
    The output files display the Surface Water Index.

    Args:
      status (dict): Status.
      conf (dict): Configuration.
    """
    # ================ #
    # 1. Init function #
    # ================ #
    # Global variable, __this
    _init(status, conf)

    # User input arguments
    arg_bbox = conf['product']['bbox']
    arg_period_s = conf['product']['period']['s']
    arg_period_e = conf['product']['period']['e']

    # Product data from base.yml
    prod_folder = conf['folder']

    prod_res = conf['product']['resolution']
    prod_freq = conf['product']['freq']

    prod_lat = conf['product']['data']['lat']
    prod_lon = conf['product']['data']['lon']

    prod_date_s = conf['product']['data']['time']['s']
    prod_date_e = conf['product']['data']['time']['s']

    prod_fname = conf['product']['data']['fname']

    # ============ #
    # 2. Check arg #
    # ============ #
    # Check the latitude and longitude, otherwise set lat or lon on greatest extent
    latlim = [np.max([arg_bbox['s'], prod_lat['s']]),
              np.min([arg_bbox['n'], prod_lat['n']])]

    lonlim = [np.max([arg_bbox['w'], prod_lon['w']]),
              np.min([arg_bbox['e'], prod_lon['e']])]

    # Check Startdate and Enddate, make a panda timestamp of the date
    if np.logical_or(arg_period_s == '', arg_period_s is None):
        date_s = pd.Timestamp(prod_date_s)
    else:
        date_s = pd.Timestamp(arg_period_s)

    if np.logical_or(arg_period_e == '', arg_period_e is None):
        if prod_date_e is None:
            date_e = pd.Timestamp.now()
        else:
            date_e = pd.Timestamp(prod_date_e)
    else:
        date_e = pd.Timestamp(arg_period_e)

    # Creates dates library
    date_dates = pd.date_range(date_s, date_e, freq=prod_freq)

    # =========== #
    # 3. Download #
    # =========== #
    # Download variables
    is_waitbar = False

    dwn_dates = date_dates
    dwn_folders = prod_folder
    dwn_fnames = prod_fname
    dwn_latlim = latlim
    dwn_lonlim = lonlim
    dwn_total = len(date_dates)
    dwn_res = prod_res

    # Download start
    status = download_product(dwn_dates,
                              dwn_folders, dwn_fnames,
                              dwn_latlim, dwn_lonlim,
                              is_waitbar, dwn_total, dwn_res)
    return status


def download_product(dates,
                     tmp_folder, tmp_fname,
                     latlim, lonlim,
                     is_waitbar, total, timestep) -> int:
    # Define local variable
    status = -1

    username = __this.username
    password = __this.password
    url_server = __this.conf['product']['url']
    tmp_url_dir = __this.conf['product']['data']['dir']

    # Define IDs
    y_id = np.int16(
        np.array([np.floor((-latlim[1]) * 10),
                  np.ceil((-latlim[0]) * 10)])) + 900
    x_id = 1800 + np.int16(
        np.array([np.ceil((lonlim[0]) * 10),
                  np.floor((lonlim[1]) * 10)]))

    # Create Waitbar
    # amount = 0
    # if is_waitbar == 1:
    #     amount = 0
    #     collect.WaitBar(amount, total,
    #                     prefix='ALEXI:', suffix='Complete',
    #                     length=50)

    for date in dates:
        # Date as printed in filename
        fname_r = tmp_fname['r'].format(dtime=date)
        if tmp_fname['t'] is not None:
            fname_t = tmp_fname['t'].format(dtime=date)
        else:
            fname_t = ''
        fname_l = tmp_fname['l'].format(dtime=date)

        file_r = os.path.join(tmp_folder['r'], fname_r)
        file_t = os.path.join(tmp_folder['t'], fname_t)
        file_l = os.path.join(tmp_folder['l'], fname_l)

        # Download the data from server
        url_dir = tmp_url_dir.format(dtime=date)
        status = start_download(file_r, file_t, file_l, fname_r,
                                lonlim, latlim, y_id, x_id, timestep,
                                url_server, url_dir, username, password)

        # Update waitbar
        # if is_waitbar == 1:
        #     amount += 1
        #     collect.WaitBar(amount, total,
        #                     prefix='Progress:', suffix='Complete',
        #                     length=50)
    return status


def start_download(remote_file, temp_file, local_file, remote_fname,
                   lonlim, latlim, y_id, x_id, timestep,
                   url_server, url_dir, username, password) -> int:
    """
    This function retrieves ALEXI data for a given date from the
    ftp.wateraccounting.unesco-ihe.org server.

    Restrictions:
    The data and this python file may not be distributed to others without
    permission of the WA+ team due data restriction of the ALEXI developers.

    Keyword arguments:

    """
    # Define local variable
    status = -1

    # Download the data from server if the file not exists
    msg = 'Downloading "{f}"'.format(f=remote_fname)
    print('{}'.format(msg))
    __this.Log.write(datetime.datetime.now(), msg=msg)

    if not os.path.exists(local_file):
        url = '{sr}{dr}{fl}'.format(sr=url_server, dr=url_dir, fl=remote_fname)
        try:
            # Download data
            try:
                req = requests.get(url, auth=HTTPBasicAuth(username, password))
                # req.raise_for_status()
            except BaseException:
                from requests.packages.urllib3.exceptions import InsecureRequestWarning
                requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
                req = requests.get(url, auth=(username, password), verify=False)

            fp = open(remote_file, 'wb')
            fp.write(req.content)
            fp.close()
        except requests.exceptions.RequestException as err:
            # Download error
            status = 1
            msg = "Not able to download {fl}, from {sr}{dr}".format(sr=url_server,
                                                                    dr=url_dir,
                                                                    fl=remote_fname)
            print('\33[91m{}\n{}\33[0m'.format(msg, str(err)))
            __this.Log.write(datetime.datetime.now(),
                             msg='{}\n{}'.format(msg, str(err)))
        else:
            # Download success
            # post-process remote (from server) -> temporary (unzip) -> local (gis)
            msg = 'Saving file "{f}"'.format(f=local_file)
            print('\33[94m{}\33[0m'.format(msg))
            __this.Log.write(datetime.datetime.now(), msg=msg)

            # load data from downloaded remote file, and clip data
            fh = Dataset(remote_file)
            data_raw = fh.variables['SWI_010']

            dataset = data_raw[:, y_id[0]: y_id[1], x_id[0]: x_id[1]]

            data = np.squeeze(dataset.data, axis=0)
            fh.close()

            # convert units, set NVD
            data = data * 0.5
            data[data > 100.] = -9999

            # save as GTiff
            geo = [lonlim[0], 0.1, 0, latlim[1], 0, -0.1]
            Save_as_tiff(name=local_file, data=data, geo=geo, projection="WGS84")

            status = 0
        finally:
            # Release local resources.
            raw_data = None
            dataset = None
            data = None
            pass
    else:
        status = 0
        msg = 'Exist "{f}"'.format(f=local_file)
        print('\33[93m{}\33[0m'.format(msg))
        __this.Log.write(datetime.datetime.now(), msg=msg)

    msg = 'Finish'
    __this.Log.write(datetime.datetime.now(), msg=msg)
    return status
