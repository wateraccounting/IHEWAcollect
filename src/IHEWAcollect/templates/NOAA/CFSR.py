# -*- coding: utf-8 -*-
"""

"""
# General modules
import os
import sys
import datetime

import requests
# from requests.auth import HTTPBasicAuth
from joblib import Parallel, delayed

import pandas as pd
import numpy as np
from netCDF4 import Dataset

# IHEWAcollect Modules
try:
    from ..collect import \
        Extract_Data_gz, Open_tiff_array, Save_as_tiff, \
        Convert_grb2_to_nc
    from ..gis import GIS
    from ..dtime import Dtime
    from ..util import Log
except ImportError:
    from IHEWAcollect.templates.collect import \
        Extract_Data_gz, Open_tiff_array, Save_as_tiff, \
        Convert_grb2_to_nc
    from IHEWAcollect.templates.gis import GIS
    from IHEWAcollect.templates.dtime import Dtime
    from IHEWAcollect.templates.util import Log


__this = sys.modules[__name__]


def _init(status, conf):
    # From download.py
    __this.status = status
    __this.conf = conf

    account = conf['account']
    folder = conf['folder']
    product = conf['product']

    # Init supported classes
    __this.GIS = GIS(status, conf)
    __this.Dtime = Dtime(status, conf)
    __this.Log = Log(conf['log'])

    return account, folder, product


def DownloadData(status, conf) -> int:
    """
    This function collects daily CFSR data in geotiff format

    Args:
      status (dict): Status.
      conf (dict): Configuration.
    """
    # ================ #
    # 1. Init function #
    # ================ #
    # Global variable, __this
    account, folder, product = _init(status, conf)

    # User input arguments
    arg_bbox = conf['product']['bbox']
    arg_period_s = conf['product']['period']['s']
    arg_period_e = conf['product']['period']['e']

    # Local variables
    is_waitbar = False

    # ============================== #
    # 2. Check latlim, lonlim, dates #
    # ============================== #
    # Check the latitude and longitude, otherwise set lat or lon on greatest extent
    latlim = [
        np.max(
            [
                arg_bbox['s'],
                product['data']['lat']['s']
            ]
        ),
        np.min(
            [
                arg_bbox['n'],
                product['data']['lat']['n']
            ]
        )
    ]

    lonlim = [
        np.max(
            [
                arg_bbox['w'],
                product['data']['lon']['w'] -
                (product['data']['lon']['e'] - product['data']['lon']['w']) / 2.0
            ]
        ),
        np.min(
            [
                arg_bbox['e'],
                product['data']['lon']['e'] -
                (product['data']['lon']['e'] - product['data']['lon']['w']) / 2.0
            ]
        )
    ]

    # Check Startdate and Enddate, make a panda timestamp of the date
    if np.logical_or(arg_period_s == '', arg_period_s is None):
        date_s = pd.Timestamp(product['data']['time']['s'])
    else:
        date_s = pd.Timestamp(arg_period_s)

    if np.logical_or(arg_period_e == '', arg_period_e is None):
        if product['data']['time']['e'] is None:
            date_e = pd.Timestamp.now()
        else:
            date_e = pd.Timestamp(product['data']['time']['e'])
    else:
        date_e = pd.Timestamp(arg_period_e)

    # Creates dates library
    date_dates = pd.date_range(date_s, date_e, freq=product['freq'])

    # =========== #
    # 3. Download #
    # =========== #
    status = download_product(latlim, lonlim, date_dates,
                              account, folder, product,
                              is_waitbar)

    return status


def download_product(latlim, lonlim, dates,
                     account, folder, product,
                     is_waitbar) -> int:
    # Define local variable
    status = -1
    total = len(dates)
    cores = 1

    # Create Waitbar
    # amount = 0
    # if is_waitbar == 1:
    #     amount = 0
    #     collect.WaitBar(amount, total,
    #                     prefix='ALEXI:', suffix='Complete',
    #                     length=50)

    if not cores:
        for date in dates:
            args = get_download_args(latlim, lonlim, date,
                                     account, folder, product)

            status = start_download(args)

            # Update waitbar
            # if is_waitbar == 1:
            #     amount += 1
            #     collect.WaitBar(amount, total,
            #                     prefix='Progress:', suffix='Complete',
            #                     length=50)
    else:
        status = Parallel(n_jobs=cores)(
            delayed(
                start_download)(
                get_download_args(
                    latlim, lonlim, date,
                    account, folder, product)) for date in dates)

    return status


def get_download_args(latlim, lonlim, date,
                      account, folder, product) -> tuple:
    # Define arg_account
    try:
        username = account['data']['username']
        password = account['data']['password']
        apitoken = account['data']['apitoken']
    except KeyError:
        username = ''
        password = ''
        apitoken = ''

    # Define arg_url
    url_server = product['url']
    url_dir = product['data']['dir'].format(dtime=date)

    # Define arg_filename
    fname_r = product['data']['fname']['r'].format(dtime=date)
    if product['data']['fname']['t'] is None:
        fname_t = ''
    else:
        fname_t = product['data']['fname']['t']
    fname_l = product['data']['fname']['l'].format(dtime=date)

    # Define arg_file
    file_r = os.path.join(folder['r'], fname_r)
    file_t = os.path.join(folder['t'], fname_t)
    file_l = os.path.join(folder['l'], fname_l)

    data_ndv = product['nodata']
    data_type = product['data']['dtype']['l']
    data_multiplier = float(product['data']['units']['m'])
    data_variable = product['data']['variable']

    # Define arg_IDs
    prod_lon_w = product['data']['lon']['w']
    prod_lat_n = product['data']['lat']['n']
    prod_lon_e = product['data']['lon']['e']
    prod_lat_s = product['data']['lat']['s']
    prod_lat_size = abs(product['data']['lat']['r'])
    prod_lon_size = abs(product['data']['lon']['r'])

    # Define arg_GTiff
    pixel_h = int(product['data']['dem']['h'])
    pixel_w = int(product['data']['dem']['w'])
    pixel_size = max(prod_lat_size, prod_lon_size)

    # Calculate arg_IDs
    prod_lat_w_shift = prod_lon_w - (prod_lon_e - prod_lon_w) / 2.0

    # [w,n]--[e,n]
    #   |      |
    # [w,s]--[e,s]
    y_id = np.int16(np.array([
        np.floor((prod_lat_n - latlim[1]) / prod_lat_size),
        np.ceil((prod_lat_n - latlim[0]) / prod_lat_size)
    ]))
    x_id = np.int16(np.array([
        np.floor((lonlim[0] - prod_lat_w_shift) / prod_lon_size),
        np.ceil((lonlim[1] - prod_lat_w_shift) / prod_lon_size)
    ]))
    # [w,s]--[e,s]
    #   |      |
    # [w,n]--[e,n]
    # y_id = np.int16(np.array([
    #     np.floor((latlim[0] - prod_lat_s) / prod_lat_size),
    #     np.ceil((latlim[1] - prod_lat_s) / prod_lat_size)
    # ]))
    # x_id = np.int16(np.array([
    #     np.floor((lonlim[0] - prod_lat_w_shift) / prod_lon_size),
    #     np.ceil((lonlim[1] - prod_lat_w_shift) / prod_lon_size)
    # ]))

    return latlim, lonlim, date, \
           product, \
           username, password, apitoken, \
           url_server, url_dir, \
           fname_r, fname_t, fname_l, \
           file_r, file_t, file_l,\
           y_id, x_id, pixel_size, pixel_w, pixel_h, \
           data_ndv, data_type, data_multiplier, data_variable


def start_download(args) -> int:
    """Retrieves data
    """
    # Unpack the arguments
    latlim, lonlim, date,\
    product, \
    username, password, apitoken, \
    url_server, url_dir, \
    remote_fname, temp_fname, local_fname,\
    remote_file, temp_file, local_file,\
    y_id, x_id, pixel_size, pixel_w, pixel_h, \
    data_ndv, data_type, data_multiplier, data_variable = args

    # Define local variable
    status = -1

    # Download the data from server if the file not exists
    if not os.path.exists(local_file):
        url = '{sr}{dr}{fn}'.format(sr=url_server, dr=url_dir, fn=remote_fname)
        # print('url: "{f}"'.format(f=url))

        try:
            # Connect to server
            msg = 'Downloading "{f}"'.format(f=remote_fname)
            print('{}'.format(msg))
            __this.Log.write(datetime.datetime.now(), msg=msg)

            # import pycurl
            # try:
            #     # Connect to server
            #     conn = pycurl.Curl()
            #     conn.setopt(pycurl.URL, url)
            #     conn.setopt(pycurl.SSL_VERIFYPEER, 0)
            #     conn.setopt(pycurl.SSL_VERIFYHOST, 0)
            # except pycurl.error as err:
            # else:
            #     with open(remote_file, "wb") as fp:
            #         conn.setopt(pycurl.WRITEDATA, fp)
            #         conn.perform()
            #         conn.close()
            try:
                conn = requests.get(url)
            except BaseException:
                from requests.packages.urllib3.exceptions import InsecureRequestWarning
                requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
                conn = requests.get(url, verify=False)
            # conn.raise_for_status()
        except requests.exceptions.RequestException as err:
            # Connect error
            status = 1
            msg = "Not able to download {fl}, from {sr}{dr}".format(sr=url_server,
                                                                    dr=url_dir,
                                                                    fl=remote_fname)
            print('\33[91m{}\n{}\33[0m'.format(msg, str(err)))
            __this.Log.write(datetime.datetime.now(),
                             msg='{}\n{}'.format(msg, str(err)))
        else:
            # Download data
            if conn.status_code == requests.codes.ok:
                if not os.path.exists(remote_file):
                    with open(remote_file, "wb") as fp:
                        fp.write(conn.content)
                        conn.close()
                else:
                    msg = 'Exist "{f}"'.format(f=remote_file)
                    print('\33[93m{}\33[0m'.format(msg))
                    __this.Log.write(datetime.datetime.now(), msg=msg)

                # Download success
                # post-process remote (from server) -> temporary (unzip) -> local (gis)
                msg = 'Saving file "{f}"'.format(f=local_file)
                print('\33[94m{}\33[0m'.format(msg))
                __this.Log.write(datetime.datetime.now(), msg=msg)

                status = convert_data(args)
            else:
                msg = "Not able to download {fl}, from {sr}{dr}".format(sr=url_server,
                                                                        dr=url_dir,
                                                                        fl=remote_fname)
                print('\33[91m{}\n{}\33[0m'.format(conn.status_code, msg))
                __this.Log.write(datetime.datetime.now(),
                                 msg='{}\n{}'.format(conn.status_code, msg))
        finally:
            # Release local resources.
            # raw_data = None
            # dataset = None
            # data = None
            pass
    else:
        status = 0
        msg = 'Exist "{f}"'.format(f=local_file)
        print('\33[93m{}\33[0m'.format(msg))
        __this.Log.write(datetime.datetime.now(), msg=msg)

    msg = 'Finish'
    __this.Log.write(datetime.datetime.now(), msg=msg)
    return status


def convert_data(args):
    """
    """
    # Unpack the arguments
    latlim, lonlim, date,\
    product, \
    username, password, apitoken, \
    url_server, url_dir, \
    remote_fname, temp_fname, local_fname,\
    remote_file, temp_file, local_file,\
    y_id, x_id, pixel_size, pixel_w, pixel_h, \
    data_ndv, data_type, data_multiplier, data_variable = args

    # Define local variable
    status = -1
    nparts = 4

    # Load data from downloaded remote file

    # Generate temporary files
    for i in range(0, nparts):
        # Band number of the grib data which is converted in .nc
        temp_file_part = temp_file.format(dtime=date, ipart=str(i + 1))
        temp_file_band = (int(date.strftime('%d')) - 1) * 28 + (i + 1) * 7

        Convert_grb2_to_nc(remote_file, temp_file_part, temp_file_band)

    # Load data from temporary files
    for i in range(0, nparts):
        temp_file_part = temp_file.format(dtime=date, ipart=str(i + 1))

        fp = Dataset(temp_file_part, mode='r')

        data_raw = fp.variables['Band1']

        if 'missing_value' in data_raw.ncattrs():
            data_raw_missing = data_raw.getncattr('missing_value')
        else:
            data_raw_missing = data_raw.getncattr('_FillValue')
        if 'scale_factor' in data_raw.ncattrs():
            data_raw_scale = data_raw.getncattr('scale_factor')
        else:
            data_raw_scale = 1.0

        data_raw = np.zeros([pixel_h, pixel_w])
        data_raw = data_raw + np.array(fp.variables['Band1'][0:pixel_h, 0:pixel_w])

        fp.close()
    # calculate the average
    data_raw = data_raw / float(nparts)

    data_tmp = np.zeros([pixel_h, pixel_w])
    data_tmp[:, 0:int(pixel_w / 2)] = data_raw[:, int(pixel_w / 2):pixel_w]
    data_tmp[:, int(pixel_w / 2):pixel_w] = data_raw[:, 0:int(pixel_w / 2)]

    # Clip data
    data = np.flipud(data_tmp[y_id[0]:y_id[1], x_id[0]:x_id[1]])

    # Check data type
    # filled numpy.ma.MaskedArray as numpy.ndarray
    if isinstance(data, np.ma.MaskedArray):
        data = data.filled()
    else:
        data = np.asarray(data)
    # convert to float
    if np.logical_or(isinstance(data_raw_missing, str),
                     isinstance(data_raw_scale, str)):
        data_raw_missing = float(data_raw_missing)
        data_raw_scale = float(data_raw_scale)

    # Convert units, set NVD
    data[data == data_raw_missing] = np.nan
    data = data * data_raw_scale * data_multiplier

    data[data == np.nan] = data_ndv

    # Save as GTiff
    geo = [lonlim[0], pixel_size, 0, latlim[1], 0, -pixel_size]
    Save_as_tiff(name=local_file, data=data, geo=geo, projection="WGS84")

    status = 0
    return status
