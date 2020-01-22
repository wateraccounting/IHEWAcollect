# -*- coding: utf-8 -*-
"""
**ALEXI**

`Restrictions`

The data and this python file may not be distributed to others without
permission of the WA+ team.

`Description`

This module downloads ALEXI data from
``ftp.wateraccounting.unesco-ihe.org``.

Use the ALEXI.daily function to download
and create weekly ALEXI images in Gtiff format.

The data is available between ``2003-01-01 till 2015-12-31``.

The output file with the name ``2003.01.01`` contains
the **total evaporation** in ``mm`` for the period of ``1 January - 7 January``.

**Examples:**
::

    from IHEWAcollect import ALEXI
    ALEXI.daily(Dir='C:/Temp/',
                Startdate='2003-12-01', Enddate='2004-01-20',
                latlim=[-10, 30], lonlim=[-20, -10])
"""
# General modules
import os
import sys
# import glob
# import shutil

import math
import datetime

from urllib.parse import urlparse
from ftplib import FTP, all_errors

import numpy as np
import pandas as pd
# from netCDF4 import Dataset

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


def init(status, conf):
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


def DownloadData(status, conf) -> dict:
    """Downloads ALEXI ET data

    This scripts downloads ALEXI ET data from the UNESCO-IHE ftp server.
    The output files display the total ET in mm for a period of one week.
    The name of the file corresponds to the first day of the week.

    Args:
      status (dict): Status.
      conf (dict): Configuration.

    Returns:
      str: TimeStep, 'daily' or 'weekly'.
    """
    # ================ #
    # 1. Init function #
    # ================ #
    # Global variable, __this
    init(status, conf)

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

    # Local variable
    is_waitbar = False

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

    # Check resolution,
    # Define the Start date of ALEXI
    if prod_res == 'weekly':
        date_doy = date_s.timetuple().tm_yday
        date_year = date_s.timetuple().tm_year

        # Change the startdate so it includes an ALEXI date
        date_doy_s = int(math.ceil(date_doy / 7.0) * 7 + 1)

        # Stringify date DOY start
        date_doy_s = '{doy}-{yr}'.format(doy=date_doy_s, yr=date_year)

        date_day = datetime.datetime.strptime(date_doy_s, '%j-%Y')
        date_month = '%02d' % date_day.month
        date_day = '%02d' % date_day.day
        date = (str(date_year) + '-' + str(date_month) + '-' + str(date_day))

        # String to datetime
        date_doy = datetime.datetime.strptime(date,
                                              '%Y-%m-%d').timetuple().tm_yday
        date = pd.Timestamp(date)

        # amount of Dates weekly
        date_dates = pd.date_range(date, date_e, freq=prod_freq)

    elif prod_res == 'daily':
        date_dates = pd.date_range(date_s, date_e, freq=prod_freq)

    else:
        raise ValueError('{err} not support.'.format(err=prod_res))

    # =========== #
    # 3. Download #
    # =========== #
    if prod_res == 'weekly':
        dwn_date = date

    dwn_dates = date_dates
    dwn_end = date_e
    dwn_nfile = date_e
    dwn_folders = prod_folder
    dwn_fnames = prod_fname
    dwn_latlim = latlim
    dwn_lonlim = lonlim
    dwn_res = prod_res

    # Create Waitbar
    date_total_amount = len(date_dates)
    # if is_waitbar == 1:
    #     amount = 0
    #     collect.WaitBar(amount, total_amount,
    #                     prefix='ALEXI:', suffix='Complete',
    #                     length=50)

    if prod_res == 'weekly':
        status = ALEXI_weekly(dwn_date, dwn_end,
                              dwn_folders, dwn_fnames,
                              dwn_latlim, dwn_lonlim,
                              date_year,
                              is_waitbar, dwn_nfile, dwn_res)

    if prod_res == 'daily':
        status = ALEXI_daily(dwn_dates,
                             dwn_folders, dwn_fnames,
                             dwn_latlim, dwn_lonlim,
                             is_waitbar, dwn_nfile, dwn_res)

    return status


def ALEXI_daily(dates,
                tmp_folder, tmp_fname,
                latlim, lonlim,
                is_waitbar, total, timestep) -> int:
    status = -1

    # Define local variable
    amount = 0

    # Define IDs
    y_id = 3000 - np.int16(
        np.array([np.ceil((latlim[1] + 60) * 20), np.floor((latlim[0] + 60) * 20)]))
    x_id = np.int16(
        np.array([np.floor((lonlim[0]) * 20), np.ceil((lonlim[1]) * 20)]) + 3600)

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
        status = Download_ALEXI_from_WA_FTP(file_r, file_t, file_l, fname_r,
                                            lonlim, latlim, y_id, x_id,
                                            timestep)

        # # Adjust waitbar
        # if is_waitbar == 1:
        #     amount += 1
        #     collect.WaitBar(amount, total_amount,
        #                     prefix='ALEXI:', suffix='Complete',
        #                     length=50)
    return status


def ALEXI_weekly(date, dates_e,
                 tmp_folder, tmp_fname,
                 latlim, lonlim,
                 date_year,
                 is_waitbar, total, timestep) -> int:
    status = -1

    # Define local variable
    amount = 0

    # Define the stop conditions
    Stop = dates_e.toordinal()
    End_date = 0

    # Define IDs
    y_id = 3000 - np.int16(
        np.array([np.ceil((latlim[1] + 60) * 20), np.floor((latlim[0] + 60) * 20)]))
    x_id = np.int16(
        np.array([np.floor((lonlim[0]) * 20), np.ceil((lonlim[1]) * 20)]) + 3600)

    while End_date == 0:
        # Date as printed in filename
        fname_r = tmp_fname['r'].format(dtime=date)
        if tmp_fname['t'] is not None:
            fname_t = tmp_fname['t'].format(dtime=date)
        else:
            fname_t = ''
        fname_l = tmp_fname['l'].format(dtime=date + pd.DateOffset(days=-7))

        file_r = os.path.join(tmp_folder['r'], fname_r)
        file_t = os.path.join(tmp_folder['t'], fname_t)
        file_l = os.path.join(tmp_folder['l'], fname_l)

        # Download the data from server
        status = Download_ALEXI_from_WA_FTP(file_r, file_t, file_l, fname_r,
                                            lonlim, latlim, y_id, x_id,
                                            timestep)

        # Create the new date for the next download
        Datename = (str(date.strftime('%Y')) + '-' + str(
            date.strftime('%m')) + '-' + str(date.strftime('%d')))
        DOY = datetime.datetime.strptime(Datename,
                                         '%Y-%m-%d').timetuple().tm_yday

        # Define next day
        DOY_next = int(DOY + 7)
        if DOY_next >= 366:
            DOY_next = 8
            date_year += 1
        DOYnext = str('%s-%s' % (DOY_next, date_year))
        DayNext = datetime.datetime.strptime(DOYnext, '%j-%Y')
        Month = '%02d' % DayNext.month
        Day = '%02d' % DayNext.day
        date = (str(date_year) + '-' + str(Month) + '-' + str(Day))

        # Check if this file must be downloaded
        date = pd.Timestamp(date)
        if date.toordinal() > Stop:
            End_date = 1

        # # Adjust waitbar
        # if is_waitbar == 1:
        #     amount += 1
        #     collect.WaitBar(amount, total_amount,
        #                     prefix='ALEXI:', suffix='Complete',
        #                     length=50)
    return status


def Download_ALEXI_from_WA_FTP(remote_file, temp_file, local_file, remote_fname,
                               lonlim, latlim, y_id, x_id, timestep) -> int:
    """Retrieves ALEXI data

    This function retrieves ALEXI data for a given date from the
    `<ftp.wateraccounting.unesco-ihe.org>`_ server.

    Args:
      local_filename (str): name of the temporary file which contains global ALEXI data.
      DirFile (str): name of the end file with the weekly ALEXI data.
      filename (str): name of the end file.
      latlim (list): [ymin, ymax] (values must be between -60 and 70).
      lonlim (list): [xmin, xmax] (values must be between -180 and 180).
      yID (list): latlim to index.
      xID (list): lonlim to index.
      TimeStep (str): 'daily' or 'weekly'  (by using here monthly,
        an older dataset will be used).
    """
    status = -1

    msg = 'Downloading "{f}"'.format(f=remote_fname)
    print('{}'.format(msg))
    __this.Log.write(datetime.datetime.now(), msg=msg)
    if not os.path.exists(local_file):
        try:
            # Collect url
            # with "ftp://" -> "[Errno 11001] getaddrinfo failed"
            # url_server = __this.conf['product']['url']
            # without "ftp://" -> Pass
            url_server = urlparse(__this.conf['product']['url']).netloc
            url_dir = __this.conf['product']['data']['dir']

            # Access server
            ftp = FTP(url_server)
            ftp.login(__this.username, __this.password)
            ftp.cwd(url_dir)

            # Download data
            lf = open(remote_file, "wb")
            ftp.retrbinary("RETR " + remote_fname, lf.write)
            lf.close()
        except all_errors as err:
            status = 1
            msg = "Not able to download file, from {sr}{dr}".format(sr=url_server,
                                                                    dr=url_dir)
            print('\33[91m{}\n{}\33[0m'.format(msg, str(err)))
            __this.Log.write(datetime.datetime.now(),
                             msg='{}\n{}'.format(msg, str(err)))
        else:
            # Post-process
            # remote (from server) -> temporary (unzip) -> local (gis)
            if timestep == "daily":
                Extract_Data_gz(remote_file, temp_file)

                raw_data = np.fromfile(temp_file, dtype="<f4")

                dataset = np.flipud(np.resize(raw_data, [3000, 7200]))
                # Values are in MJ/m2d so convert to mm/d
                data = dataset[y_id[0]:y_id[1], x_id[0]:x_id[1]] / 2.45  # mm/d
                data[data < 0] = -9999

            if timestep == "weekly":
                # Open global ALEXI data
                dataset = Open_tiff_array(remote_file)

                # Clip extend out of world data
                data = dataset[y_id[0]:y_id[1], x_id[0]:x_id[1]]
                data[data < 0] = -9999

            # final GTiff
            geo = [lonlim[0], 0.05, 0, latlim[1], 0, -0.05]
            Save_as_tiff(name=local_file, data=data, geo=geo, projection="WGS84")

            status = 0
            msg = 'Finish "{f}"'.format(f=local_file)
            print('\33[94m{}\33[0m'.format(msg))
            __this.Log.write(datetime.datetime.now(), msg=msg)
        finally:
            # Release local resources.
            pass
    else:
        status = 0
        msg = 'Exist "{f}"'.format(f=local_file)
        print('\33[93m{}\33[0m'.format(msg))
        __this.Log.write(datetime.datetime.now(), msg=msg)

    return status
