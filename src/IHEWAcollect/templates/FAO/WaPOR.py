# -*- coding: utf-8 -*-
"""
**WaPOR Module**

"""
# General modules
import os
import sys
import datetime

# import paramiko
# from urllib.parse import urlparse
from joblib import Parallel, delayed

import numpy as np
import pandas as pd
# from netCDF4 import Dataset

# IHEWAcollect Modules
try:
    from ..collect import \
        Convert_hdf5_to_tiff, Clip_Dataset_GDAL, Merge_Dataset_GDAL, \
        Open_array_info, Open_tiff_array, Save_as_tiff

    from ..gis import GIS
    from ..dtime import Dtime
    from ..util import Log
except ImportError:
    from IHEWAcollect.templates.collect import \
        Convert_hdf5_to_tiff, Clip_Dataset_GDAL, Merge_Dataset_GDAL, \
        Open_array_info, Open_tiff_array, Save_as_tiff

    from IHEWAcollect.templates.gis import GIS
    from IHEWAcollect.templates.dtime import Dtime
    from IHEWAcollect.templates.util import Log


__this = sys.modules[__name__]


def _init(status, conf):
    # From download.py
    __this.status = status
    __this.conf = conf
    __this.path = os.path.join(
        os.getcwd(),
        os.path.dirname(
            inspect.getfile(
                inspect.currentframe()))
    )

    account = conf['account']
    folder = conf['folder']
    product = conf['product']

    # Init supported classes
    __this.GIS = GIS(status, conf)
    __this.Dtime = Dtime(status, conf)
    __this.Log = Log(conf['log'])

    return account, folder, product


def DownloadData(status, conf) -> int:
    """This is main interface.

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
    if np.logical_or(pd.Timestamp(date_s) is pd.NaT,
                     pd.Timestamp(date_e) is pd.NaT):
        date_s = pd.Timestamp.now()
        date_e = pd.Timestamp.now()

    if product['freq'] is None:
        date_dates = pd.date_range(date_e, date_e, periods=1)
    elif 'D' in product['freq']:
        freq = np.fromstring(product['freq'], dtype=float, sep='D')
        if len(freq) > 0:
            date_s_doy = int(np.floor(date_s.dayofyear / freq[0])) * int(freq[0]) + 1
            date_e_doy = int(np.floor(date_e.dayofyear / freq[0])) * int(freq[0]) + 1

            date_s = pd.to_datetime('{}-{}'.format(date_s.year, date_s_doy),
                                    format='%Y-%j')
            date_e = pd.to_datetime('{}-{}'.format(date_e.year, date_e_doy),
                                    format='%Y-%j')

            date_years = date_e.year - date_s.year
            if date_years > 0:
                date_s_year = date_s.year

                i = 0
                date_ey = pd.Timestamp('{}-12-31'.format(date_s_year + i))
                date_dates = pd.date_range(
                    date_s, date_ey, freq=product['freq'])

                for i in range(1, date_years):
                    date_sy = pd.Timestamp('{}-01-01'.format(date_s_year + i))
                    date_ey = pd.Timestamp('{}-12-31'.format(date_s_year + i))
                    date_dates = date_dates.union(pd.date_range(
                        date_sy, date_ey, freq=product['freq']))

                i = date_years
                date_sy = pd.Timestamp('{}-01-01'.format(date_s_year + i))
                date_dates = date_dates.union(pd.date_range(
                    date_sy, date_e, freq=product['freq']))
            else:
                date_dates = pd.date_range(date_s, date_e, freq=product['freq'])
        else:
            date_dates = pd.date_range(date_s, date_e, freq=product['freq'])
    else:
        date_dates = pd.date_range(date_s, date_e, freq=product['freq'])

    # =========== #
    # 3. Download #
    # =========== #
    status_cod = download_product(latlim, lonlim, date_dates,
                                  account, folder, product,
                                  is_waitbar)

    return status_cod

def download_product(latlim, lonlim, dates,
                     account, folder, product,
                     is_waitbar) -> int:
    # Define local variable
    status_cod = -1
    # total = len(dates)

    cores = -1

    arg1 = product_details(latlim, lonlim, account, product)
    if not cores:
        for date in dates:
            arg2 = get_download_args(latlim, lonlim, date,
                                     folder, product)
           
            args = arg2+arg1
            
            status_cod = start_download(args)

            # Update waitbar
            # if is_waitbar == 1:
            #     amount += 1
            #     collect.WaitBar(amount, total,
            #                     prefix='Progress:', suffix='Complete',
            #                     length=50)
    else:
        status_cod = Parallel(n_jobs=cores)(
            delayed(start_download)(get_download_args(
                    latlim, lonlim, date,
                    folder, product)+arg1) for date in dates)
        
    return status_cod

def get_download_args(latlim, lonlim, date,
                      account, folder, product) -> tuple:
    msg = 'Collecting  "{f}"'.format(f=date)
    print('\33[95m{}\33[0m'.format(msg))
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
    status_cod = -1
    remote_file_status = 0
    local_file_status = 0

    return status_cod


def start_download_scan(url, username, password,
                        lat, lon) -> tuple:
    """Scan tile name
    """
    ctime = ''


def start_download_tiles(date, url_server, url_dir, username, password,
                         latlim, lonlim, fname_r, file_r) -> tuple:
    """Get tile name
    """
    url = '{sr}{dr}'.format(sr=url_server, dr=url_dir)


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
    status_cod = -1

    return status_cod


def clean(path):
    msg = 'Cleaning    "{f}"'.format(f=path)
    print('{}'.format(msg))
    __this.Log.write(datetime.datetime.now(), msg=msg)

    for root, dirs, files in os.walk(path):
        for filename in files:
            # print(filename)
            os.remove(os.path.join(root, filename))
