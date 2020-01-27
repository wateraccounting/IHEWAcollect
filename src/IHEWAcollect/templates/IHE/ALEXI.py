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
import datetime

import ftplib
from urllib.parse import urlparse
# from joblib import Parallel, delayed

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


def _init(status, conf) -> tuple:
    # test = sys.modules
    # print('GIS' in test)

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
    latlim = [np.max([arg_bbox['s'], product['data']['lat']['s']]),
              np.min([arg_bbox['n'], product['data']['lat']['n']])]

    lonlim = [np.max([arg_bbox['w'], product['data']['lon']['w']]),
              np.min([arg_bbox['e'], product['data']['lon']['e']])]

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
    if product['resolution'] == 'weekly':
        date_doy = date_s.timetuple().tm_yday
        date_year = date_s.timetuple().tm_year

        # Change the startdate so it includes an ALEXI date
        date_doy_s = int(np.ceil(date_doy / 7.0) * 7 + 1)

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
        date_dates = pd.date_range(date, date_e, freq=product['freq'])

    elif product['resolution'] == 'daily':
        date_dates = pd.date_range(date_s, date_e, freq=product['freq'])

    else:
        raise ValueError('{err} not support.'.format(err=product['freq']))

    # =========== #
    # 3. Download #
    # =========== #
    if product['resolution'] == 'daily':
        status = download_product_daily(latlim, lonlim, date_dates,
                                        account, folder, product,
                                        is_waitbar)
    if product['resolution'] == 'weekly':
        status = download_product_weekly(date, date_s, date_e,
                                         latlim, lonlim, date_dates,
                                         account, folder, product,
                                         is_waitbar)

    return status


def download_product_daily(latlim, lonlim, dates,
                           account, folder, product,
                           is_waitbar) -> int:
    # Define local variable
    status = -1
    total = len(dates)

    # Create Waitbar
    # amount = 0
    # if is_waitbar == 1:
    #     amount = 0
    #     collect.WaitBar(amount, total,
    #                     prefix='ALEXI:', suffix='Complete',
    #                     length=50)

    for date in dates:
        args = get_download_args(latlim, lonlim, date,
                                 account, folder, product)

        status = start_download(args)

        # Update waitbar
        # if is_waitbar == 1:
        #     amount += 1
        #     collect.WaitBar(amount, total,
        #                     prefix='ALEXI:', suffix='Complete',
        #                     length=50)
    return status


def download_product_weekly(date, date_s, dates_e,
                            latlim, lonlim, dates,
                            account, folder, product,
                            is_waitbar) -> int:
    # Define local variable
    status = -1
    total = len(dates)
    date_year = date_s.timetuple().tm_year

    # Create Waitbar
    # amount = 0
    # if is_waitbar == 1:
    #     amount = 0
    #     collect.WaitBar(amount, total,
    #                     prefix='Progress:', suffix='Complete',
    #                     length=50)

    # Define the stop conditions
    Stop = dates_e.toordinal()
    End_date = 0
    while End_date == 0:

        # Download the data from server

        tmp_args = get_download_args(latlim, lonlim, date,
                                     account, folder, product)

        args = []
        i = 0
        for value in tmp_args:
            if i == 8:
                url_dir = product['data']['dir'].format(
                    dtime=date + pd.DateOffset(days=-7))
            else:
                args.append(value)

        status = start_download(tuple(args))

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

        # Update waitbar
        # if is_waitbar == 1:
        #     amount += 1
        #     collect.WaitBar(amount, total,
        #                     prefix='Progress:', suffix='Complete',
        #                     length=50)
    return status


def get_download_args(latlim, lonlim, date,
                      account, folder, product) -> tuple:
    # Define arg_account
    # For download
    try:
        username = account['data']['username']
        password = account['data']['password']
        apitoken = account['data']['apitoken']
    except KeyError:
        username = ''
        password = ''
        apitoken = ''

    # Define arg_url
    url_server = urlparse(product['url']).netloc
    url_dir = product['data']['dir'].format(dtime=date)

    # Define arg_filename
    fname_r = product['data']['fname']['r'].format(dtime=date)
    if product['data']['fname']['t'] is None:
        fname_t = ''
    else:
        fname_t = product['data']['fname']['t'].format(dtime=date)
    fname_l = product['data']['fname']['l'].format(dtime=date)

    # Define arg_file
    file_r = os.path.join(folder['r'], fname_r)
    file_t = os.path.join(folder['t'], fname_t)
    file_l = os.path.join(folder['l'], fname_l)

    # Define arg_IDs
    y_id = np.int16(
        np.array([
            3000 - np.ceil((latlim[1] + 60) * 20),
            3000 - np.floor((latlim[0] + 60) * 20)
        ]))
    x_id = np.int16(
        np.array([
            np.floor((lonlim[0]) * 20) + 3600,
            np.ceil((lonlim[1]) * 20) + 3600
        ]))

    pixel_size = abs(product['data']['lat']['r'])
    # lat_pixel_size = -abs(product['data']['lat']['r'])
    # lon_pixel_size = abs(product['data']['lon']['r'])
    pixel_w = int(product['data']['dem']['w'])
    pixel_h = int(product['data']['dem']['h'])

    data_ndv = product['nodata']
    data_type = product['data']['dtype']['l']
    data_multiplier = float(product['data']['units']['m'])
    data_variable = product['data']['variable']

    return latlim, lonlim, date,\
           product, \
           username, password, apitoken, \
           url_server, url_dir, \
           fname_r, fname_t, fname_l, \
           file_r, file_t, file_l,\
           y_id, x_id, pixel_size, pixel_w, pixel_h, \
           data_ndv, data_type, data_multiplier, data_variable


def start_download(args) -> int:
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
        url = '{sr}{dr}{fn}'.format(sr=url_server, dr='', fn='')

        try:
            # Connect to server
            msg = 'Downloading "{f}"'.format(f=remote_fname)
            print('{}'.format(msg))
            __this.Log.write(datetime.datetime.now(), msg=msg)

            conn = ftplib.FTP(url)
            conn.login(username, password)
            conn.cwd(url_dir)
        except ftplib.all_errors as err:
            # Connect error
            status = 1
            msg = "Not able to download {fn}, from {sr}{dr}".format(sr=url_server,
                                                                    dr=url_dir,
                                                                    fn=remote_fname)
            print('\33[91m{}\n{}\33[0m'.format(msg, str(err)))
            __this.Log.write(datetime.datetime.now(),
                             msg='{}\n{}'.format(msg, str(err)))
        else:
            # Download data
            if not os.path.exists(remote_file):
                msg = 'Saving file "{f}"'.format(f=local_file)
                print('\33[94m{}\33[0m'.format(msg))
                __this.Log.write(datetime.datetime.now(), msg=msg)

                with open(remote_file, "wb") as fp:
                    conn.retrbinary("RETR " + remote_fname, fp.write)
            else:
                msg = 'Exist "{f}"'.format(f=remote_file)
                print('\33[93m{}\33[0m'.format(msg))
                __this.Log.write(datetime.datetime.now(), msg=msg)

            # Download success
            # post-process remote (from server) -> temporary (unzip) -> local (gis)
            status = convert_data(args)
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

    if product['resolution'] == "daily":
        # load data from downloaded remote file, and clip data
        Extract_Data_gz(remote_file, temp_file)

        data_raw = np.fromfile(temp_file, dtype="<f4")

        dataset = np.flipud(np.resize(data_raw, [pixel_h, pixel_w]))
        data = dataset[y_id[0]:y_id[1], x_id[0]:x_id[1]]

        # convert units, set Nodata Value
        data = data * data_multiplier
        data[data < 0] = data_ndv
    if product['resolution'] == "weekly":
        # load data from downloaded remote file, and clip data
        dataset = Open_tiff_array(remote_file)

        data = dataset[y_id[0]:y_id[1], x_id[0]:x_id[1]]

        # convert units, set NVD
        data[data < 0] = data_ndv

    # Save as GTiff
    geo = [lonlim[0], pixel_size, 0, latlim[1], 0, -pixel_size]
    Save_as_tiff(name=local_file, data=data, geo=geo, projection="WGS84")

    status = 0
    return status
