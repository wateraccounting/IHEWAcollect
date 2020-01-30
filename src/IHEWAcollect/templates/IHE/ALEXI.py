# -*- coding: utf-8 -*-
"""

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
    """
    # Define local variable
    status_cod = -1
    is_waitbar = False

    # ================ #
    # 1. Init function #
    # ================ #
    # Global variable, __this
    account, folder, product = _init(status, conf)

    # User input arguments
    arg_bbox = conf['product']['bbox']
    arg_period_s = conf['product']['period']['s']
    arg_period_e = conf['product']['period']['e']

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
                product['data']['lon']['w']
            ]
        ),
        np.min(
            [
                arg_bbox['e'],
                product['data']['lon']['e']
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

    if np.logical_or(pd.Timestamp(date_s) is pd.NaT,
                     pd.Timestamp(date_e) is pd.NaT):
        date_s = pd.Timestamp.now()
        date_e = pd.Timestamp.now()
        date_dates = pd.date_range(date_s, date_e)
    else:
        date_dates = pd.date_range(date_s, date_e, freq=product['freq'])

    # =========== #
    # 3. Download #
    # =========== #
    if product['resolution'] == 'daily':
        status_cod = download_product_daily(latlim, lonlim, date_dates,
                                            account, folder, product,
                                            is_waitbar)
    if product['resolution'] == 'weekly':
        status_cod = download_product_weekly(date, date_s, date_e,
                                             latlim, lonlim, date_dates,
                                             account, folder, product,
                                             is_waitbar)

    return status_cod


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
    #                     prefix='Progress:', suffix='Complete',
    #                     length=50)

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
    date_stop = dates_e.toordinal()
    date_end = 0
    while date_end == 0:

        # Download the data from server

        tmp_args = get_download_args(latlim, lonlim, date,
                                     account, folder, product)

        args = []
        i = 0
        for value in tmp_args:
            if i == 8:
                url_dir = product['data']['dir'].format(
                    dtime=date + pd.DateOffset(days=-7))
                args.append(url_dir)
            else:
                args.append(value)

        status = start_download(tuple(args))

        # Create the new date for the next download
        date_doy = date.timetuple().tm_yday
        # Define next day
        date_doy_next_int = int(date_doy + 7)
        if date_doy_next_int >= 366:
            date_doy_next_int = 8
            date_year += 1
        date_doy_next_str = str('%s-%s' % (date_doy_next_int, date_year))

        date_day_next = datetime.datetime.strptime(date_doy_next_str, '%j-%Y')
        date_month = '%02d' % date_day_next.month
        date_day = '%02d' % date_day_next.day
        date_str = (str(date_year) + '-' + str(date_month) + '-' + str(date_day))
        # Check if this file must be downloaded
        date = pd.Timestamp(date_str)
        if date.toordinal() > date_stop:
            date_end = 1

        # Update waitbar
        # if is_waitbar == 1:
        #     amount += 1
        #     collect.WaitBar(amount, total,
        #                     prefix='Progress:', suffix='Complete',
        #                     length=50)

    return status


def get_download_args(latlim, lonlim, date,
                      account, folder, product) -> tuple:
    msg = 'Collecting  "{f}"'.format(f=date)
    print('{}'.format(msg))
    __this.Log.write(datetime.datetime.now(), msg=msg)

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
    # [w,n]--[e,n]
    #   |      |
    # [w,s]--[e,s]
    y_id = np.int16(np.array([
        np.floor((prod_lat_n - latlim[1]) / prod_lat_size),
        np.ceil((prod_lat_n - latlim[0]) / prod_lat_size)
    ]))
    x_id = np.int16(np.array([
        np.floor((lonlim[0] - prod_lon_w) / prod_lon_size),
        np.ceil((lonlim[1] - prod_lon_w) / prod_lon_size)
    ]))
    # [w,s]--[e,s]
    #   |      |
    # [w,n]--[e,n]
    # y_id = np.int16(np.array([
    #     np.floor((latlim[0] - prod_lat_s) / prod_lat_size),
    #     np.ceil((latlim[1] - prod_lat_s) / prod_lat_size)
    # ]))
    # x_id = np.int16(np.array([
    #     np.floor((lonlim[0] - prod_lon_w) / prod_lon_size),
    #     np.ceil((lonlim[1] - prod_lon_w) / prod_lon_size)
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
    latlim, lonlim, date, \
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
    msg = 'Downloading "{f}"'.format(f=remote_fname)
    print('{}'.format(msg))
    __this.Log.write(datetime.datetime.now(), msg=msg)

    is_download = True
    if os.path.exists(remote_file):
        if np.ceil(os.stat(remote_file).st_size / 1024) > 0:
            is_download = False

            msg = 'Exist "{f}"'.format(f=remote_file)
            print('\33[93m{}\33[0m'.format(msg))
            __this.Log.write(datetime.datetime.now(), msg=msg)

    is_start_download = True
    if os.path.exists(local_file):
        if np.ceil(os.stat(local_file).st_size / 1024) > 0:
            is_start_download = False

            msg = 'Exist "{f}"'.format(f=local_file)
            print('\33[92m{}\33[0m'.format(msg))
            __this.Log.write(datetime.datetime.now(), msg=msg)

    if is_start_download:
        url_parse = urlparse(url_server)
        url_host = url_parse.hostname
        url_port = url_parse.port
        url = '{sr}{dr}{fn}'.format(sr=url_host, dr='', fn='')
        # print('url: "{f}"'.format(f=url))

        if is_download:
            try:
                # Connect to server
                conn = ftplib.FTP(url)
                # conn.login()
                conn.login(username, password)
                conn.cwd(url_dir)

                # listing = []
                # conn.retrlines("LIST", listing.append)
                # print(listing)
            except ftplib.all_errors as err:
                # Connect error
                status = 1
                msg = 'Not able to download {fn}, from {sr}{dr}'.format(
                    sr=url_server,
                    dr=url_dir,
                    fn=remote_fname)
                print('\33[91m{}\n{}\33[0m'.format(msg, str(err)))
                __this.Log.write(datetime.datetime.now(),
                                 msg='{}\n{}'.format(msg, str(err)))
            else:
                # Download data
                with open(remote_file, "wb") as fp:
                    conn.retrbinary("RETR " + remote_fname, fp.write)
                    conn.close()

                # Download success
                status = convert_data(args)
            finally:
                # Release local resources.
                # raw_data = None
                # dataset = None
                # data = None
                pass
    else:
        status = 0

    msg = 'Finish'
    __this.Log.write(datetime.datetime.now(), msg=msg)
    return status


def convert_data(args):
    """
    """
    # Unpack the arguments
    latlim, lonlim, date, \
        product, \
        username, password, apitoken, \
        url_server, url_dir, \
        remote_fname, temp_fname, local_fname,\
        remote_file, temp_file, local_file,\
        y_id, x_id, pixel_size, pixel_w, pixel_h, \
        data_ndv, data_type, data_multiplier, data_variable = args

    # Define local variable
    status = -1

    # post-process remote (from server)
    #  -> temporary (unzip)
    #   -> local (gis)
    msg = 'Converting  "{f}"'.format(f=local_file)
    print('\33[94m{}\33[0m'.format(msg))
    __this.Log.write(datetime.datetime.now(), msg=msg)

    if product['resolution'] == "daily":
        # Load data from downloaded remote file

        # Generate temporary files
        temp_file_part = temp_file.format(dtime=date)

        Extract_Data_gz(remote_file, temp_file_part)

        data_raw = np.fromfile(temp_file_part, dtype="<f4")

        data_tmp = np.resize(data_raw, [pixel_h, pixel_w])

        # Clip data
        data = np.flipud(data_tmp[y_id[0]:y_id[1], x_id[0]:x_id[1]])

    if product['resolution'] == "weekly":
        # Load data from downloaded remote file
        data_raw = Open_tiff_array(remote_file)

        # Generate temporary files

        # Clip data
        data = data_raw[y_id[0]:y_id[1], x_id[0]:x_id[1]]

    # Check data type
    # filled numpy.ma.MaskedArray as numpy.ndarray
    if isinstance(data, np.ma.MaskedArray):
        data = data.filled()
    else:
        data = np.asarray(data)
    # convert to float
    # if np.logical_or(isinstance(data_raw_missing, str),
    #                  isinstance(data_raw_scale, str)):
    #     data_raw_missing = float(data_raw_missing)
    #     data_raw_scale = float(data_raw_scale)

    # Convert units, set NVD
    data[data < 0] = np.nan
    data = data * data_multiplier

    data[data == np.nan] = data_ndv

    # Save as GTiff
    geo = [lonlim[0], pixel_size, 0, latlim[1], 0, -pixel_size]
    Save_as_tiff(name=local_file, data=data, geo=geo, projection="WGS84")

    status = 0
    return status
