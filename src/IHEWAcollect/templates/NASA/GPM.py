# -*- coding: utf-8 -*-
"""
**GPM Module**

"""
import datetime
# General modules
import os
import sys

import numpy as np
import pandas as pd
import requests
# from requests.auth import HTTPBasicAuth => .netrc
from joblib import Parallel, delayed
from netCDF4 import Dataset

# IHEWAcollect Modules
try:
    from ..collect import \
        Save_as_tiff

    from ..gis import GIS
    from ..dtime import Dtime
    from ..util import Log
except ImportError:
    from IHEWAcollect.templates.collect import \
        Save_as_tiff

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
    cores = 1#-1

    # Create Waitbar
    # amount = 0
    # if is_waitbar == 1:
    #     amount = 0
    #     collect.WaitBar(amount, total,
    #                     prefix='Progress:', suffix='Complete',
    #                     length=50)

    if not cores:
        for date in dates:
            args = get_download_args(latlim, lonlim, date,
                                     account, folder, product)

            status_cod = start_download(args)

            # Update waitbar
            # if is_waitbar == 1:
            #     amount += 1
            #     collect.WaitBar(amount, total,
            #                     prefix='Progress:', suffix='Complete',
            #                     length=50)
    else:
        status_cod = Parallel(n_jobs=cores)(
            delayed(
                start_download)(
                get_download_args(
                    latlim, lonlim, date,
                    account, folder, product)) for date in dates)

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

    # Define arg_url
    url_server = product['url']

    # url_dir
    fmt_d = product['data']['fmt']['d']
    if fmt_d is None:
        if product['data']['dir'] is None:
            url_dir = '/'
        else:
            url_dir = product['data']['dir']
    else:
        if 'dtime' == fmt_d:
            url_dir = product['data']['dir'].format(dtime=date)
        else:
            url_dir = product['data']['dir']

    # Define arg_filename
    # remote_fname
    fmt_r = product['data']['fmt']['r']
    if fmt_r is None:
        if product['data']['fname']['r'] is None:
            fname_r = ''
        else:
            fname_r = product['data']['fname']['r']
    else:
        if 'dtime' == fmt_r:
            fname_r = product['data']['fname']['r'].format(dtime=date)
        else:
            fname_r = product['data']['fname']['r']

    # temp_fname
    fmt_t = product['data']['fmt']['t']
    if fmt_t is None:
        if product['data']['fname']['t'] is None:
            fname_t = ''
        else:
            fname_t = product['data']['fname']['t']
    else:
        if 'dtime' == fmt_t:
            fname_t = product['data']['fname']['t'].format(dtime=date)
        else:
            fname_t = product['data']['fname']['t']

    # local_fname
    fname_l = product['data']['fname']['l'].format(dtime=date)

    # Define arg_file
    file_r = os.path.join(folder['r'], fname_r)
    file_t = os.path.join(folder['t'], fname_t)
    file_l = os.path.join(folder['l'], fname_l)

    data_ndv = product['nodata']
    data_type = product['data']['dtype']['l']
    data_multiplier = float(product['data']['units']['m'])
    if (product['freq'] is not None) and ('D' not in product['freq']):
        data_multiplier = data_multiplier*date.days_in_month

    data_variable = product['data']['variable']

    # Define arg_IDs
    prod_lon_w = product['data']['lon']['w']
    # prod_lat_n = product['data']['lat']['n']
    # prod_lon_e = product['data']['lon']['e']
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
    # y_id = np.array([
    #     np.floor((prod_lat_n - latlim[1]) / prod_lat_size),
    #     np.ceil((prod_lat_n - latlim[0]) / prod_lat_size)
    # ], dtype=np.int)
    # x_id = np.array([
    #     np.floor((lonlim[0] - prod_lon_w) / prod_lon_size),
    #     np.ceil((lonlim[1] - prod_lon_w) / prod_lon_size)
    # ], dtype=np.int)

    # [w,s]--[e,s]
    #   |      |
    # [w,n]--[e,n]
    # y_id = np.array([
    #     np.floor((latlim[0] - prod_lat_s) / prod_lat_size),
    #     np.ceil((latlim[1] - prod_lat_s) / prod_lat_size)
    # ], dtype=np.int)
    # x_id = np.array([
    #     np.floor((lonlim[0] - prod_lon_w) / prod_lon_size),
    #     np.ceil((lonlim[1] - prod_lon_w) / prod_lon_size)
    # ], dtype=np.int)

    # [w,n]--[w,s]
    #   |      |
    # [e,n]--[e,s]
    # y_id = np.array([
    #     np.floor((lonlim[0] - prod_lon_w) / prod_lon_size),
    #     np.ceil((lonlim[1] - prod_lon_w) / prod_lon_size)
    # ], dtype=np.int)
    # x_id = np.array([
    #     np.floor((prod_lat_n - latlim[1]) / prod_lat_size),
    #     np.ceil((prod_lat_n - latlim[0]) / prod_lat_size)
    # ], dtype=np.int)

    # [w,s]--[w,n]
    #   |      |
    # [e,s]--[e,n]


    y_id = np.array([
        np.floor((lonlim[0] - prod_lon_w) / prod_lon_size),
        np.ceil((lonlim[1] - prod_lon_w) / prod_lon_size)
    ], dtype=np.int)
    x_id = np.array([
        np.floor((latlim[0] - prod_lat_s) / prod_lat_size),
        np.ceil((latlim[1] - prod_lat_s) / prod_lat_size)
    ], dtype=np.int)


   # Adjust the lon, lat limits based on the grids of the data
    lonlim = np.array([
        (y_id[0] * prod_lon_size + prod_lon_w),
        (y_id[1] * prod_lon_size + prod_lon_w)
    ], dtype=np.float)
    latlim = np.array([
        (x_id[0] * prod_lat_size + prod_lat_s),
        (x_id[1] * prod_lat_size + prod_lat_s)
    ], dtype=np.float)

     # Define IDs
    # x_id = np.int16(np.array([np.ceil((latlim[0] + 90)*10),
    #                                np.floor((latlim[1] + 90)*10)]))
    # y_id = np.int16(np.array([np.floor((lonlim[0])*10),
    #                          np.ceil((lonlim[1])*10)]) + 1800)
    # print(lonlim,latlim)
    # print(prod_lon_w,prod_lat_s, prod_lon_size, prod_lat_size)
    # print(x_id,y_id)

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
    status_cod = -1
    remote_file_status = 0
    local_file_status = 0

    is_start_download = True
    if os.path.exists(local_file):
        if np.ceil(os.stat(local_file).st_size / 1024) > 0:
            is_start_download = False

            msg = 'Exist "{f}"'.format(f=local_file)
            print('\33[92m{}\33[0m'.format(msg))
            __this.Log.write(datetime.datetime.now(), msg=msg)

    if is_start_download:
        # https://disc.gsfc.nasa.gov/data-access#python
        # C:\Users\qpa001\.netrc
        file_conn_auth = os.path.join(os.path.expanduser("~"), ".netrc")
        with open(file_conn_auth, 'w+') as fp:
            fp.write('machine {m} login {u} password {p}\n'.format(
                m='urs.earthdata.nasa.gov',
                u=username,
                p=password
            ))

        # Download the data from server if the file not exists
        msg = 'Downloading "{f}"'.format(f=remote_fname)
        # print('{}'.format(msg))
        __this.Log.write(datetime.datetime.now(), msg=msg)

        is_download = True
        if os.path.exists(remote_file):
            if np.ceil(os.stat(remote_file).st_size / 1024) > 0:
                is_download = False

                msg = 'Exist "{f}"'.format(f=remote_file)
                print('\33[93m{}\33[0m'.format(msg))
                __this.Log.write(datetime.datetime.now(), msg=msg)

        # ------------- #
        # Download data #
        # ------------- #
        if is_download:
            url = '{sr}{dr}{fl}'.format(sr=url_server,
                                        dr=url_dir,
                                        fl=remote_fname)
            # print('url: "{f}"'.format(f=url))

            try:
                # Connect to server
                conn = requests.get(url) 
                conn.raise_for_status()
            except requests.exceptions.RequestException as err:
                # Connect error
                msg = 'Not able to download {fn}, from {sr}{dr}'.format(
                    sr=url_server,
                    dr=url_dir,
                    fn=remote_fname)
                print('\33[91m{}\n{}\33[0m'.format(msg, str(err)))
                __this.Log.write(datetime.datetime.now(),
                                 msg='{}\n{}'.format(msg, str(err)))
                remote_file_status += 1
            else:
                # Fetch data
                # conn.status_code == requests.codes.ok
                with open(remote_file, 'wb') as fp:
                    fp.write(conn.content)
                    conn.close()
                    remote_file_status += 0
        else:
            remote_file_status += 0

        # ---------------- #
        # Download success #
        # ---------------- #
        if remote_file_status == 0:
            local_file_status = convert_data(args)

        # --------------- #
        # Download finish #
        # --------------- #
        # raw_data = None
        # dataset = None
        # data = None
    else:
        local_file_status = 0

    status_cod = remote_file_status + local_file_status

    msg = 'Finish'
    __this.Log.write(datetime.datetime.now(), msg=msg)
    return status_cod


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

    # post-process remote (from server)
    #  -> temporary (unzip)
    #   -> local (gis)
    msg = 'Converting  "{f}"'.format(f=local_file)
   #print('\33[94m{}\33[0m'.format(msg))
    #__this.Log.write(datetime.datetime.now(), msg=msg)

    # --------- #
    # Load data #
    # --------- #
    # From downloaded remote file
    fh = Dataset(remote_file, mode='r')

    data_group = product['data']['ftype']['r'].split('.')
    if len(data_group) > 1:
        data_raw = fh.groups[data_group[1]].variables[data_variable]
    else:
        data_raw = fh.variables[data_variable]

    if 'missing_value' in data_raw.ncattrs():
        # ASCAT
        data_raw_missing = data_raw.getncattr('missing_value')
    elif 'CodeMissingValue' in data_raw.ncattrs():
        # GPM
        data_raw_missing = data_raw.getncattr('CodeMissingValue')
    else:
        data_raw_missing = data_raw.getncattr('_FillValue')
    if 'scale_factor' in data_raw.ncattrs():
        data_raw_scale = data_raw.getncattr('scale_factor')
    else:
        data_raw_scale = 1.0

    # From generated temporary file
    # Generate temporary files

    # Convert meta data to float
    if np.logical_or(isinstance(data_raw_missing, str),
                     isinstance(data_raw_scale, str)):
        data_raw_missing = float(data_raw_missing)
        data_raw_scale = float(data_raw_scale)

    # --------- #
    # Clip data #
    # --------- #
    # get data to 2D matrix
    date_id = 0
    data_tmp = data_raw[date_id, y_id[0]:y_id[1], x_id[0]:x_id[1]]
    # data_tmp = np.squeeze(data_tmp, axis=0)

    # check data type
    # filled numpy.ma.MaskedArray as numpy.ndarray
    if isinstance(data_tmp, np.ma.MaskedArray):
        data = data_tmp.filled()
    else:
        data = np.asarray(data_tmp)

    # transfer matrix to GTiff matrix
    # [w,n]--[e,n]
    #   |      |
    # [w,s]--[e,s]
    # data = np.asarray(data)

    # [w,s]--[e,s]
    #   |      |
    # [w,n]--[e,n]
    # data = np.flipud(data)

    # [w,n]--[w,s]
    #   |      |
    # [e,n]--[e,s]
    # data = np.transpose(a=data, axes=(1, 0))

    # [w,s]--[w,n]
    #   |      |
    # [e,s]--[e,n]
    data = np.rot90(data, k=1, axes=(0, 1))

    # close file
    fh.close()

    # ------- #
    # Convert #
    # ------- #
    # scale, units
    data = np.where(data == data_raw_missing, np.nan, data)
    data = data * data_raw_scale * data_multiplier

    # novalue data
    data = np.where(np.isnan(data), data_ndv, data)

    # ------------ #
    # Saveas GTiff #
    # ------------ #
    geo = [lonlim[0], pixel_size, 0,
           latlim[1], 0, -pixel_size]
    Save_as_tiff(name=local_file, data=data, geo=geo, projection="WGS84")

    if __this.conf['is_save_remote']:
        pass
    else:
        path = os.path.dirname(os.path.realpath(remote_file))
        if 'remote' != path[-6:]:
            path = os.path.join(path, 'remote')
        clean(path)
    if __this.conf['is_save_temp']:
        pass
    else:
        path = os.path.dirname(os.path.realpath(temp_file))
        if 'temporary' != path[-9:]:
            path = os.path.join(path, 'temporary')
        clean(path)

    status_cod = 0
    return status_cod


def clean(path):
    msg = 'Cleaning    "{f}"'.format(f=path)
    # print('{}'.format(msg))
    __this.Log.write(datetime.datetime.now(), msg=msg)

    for root, dirs, files in os.walk(path):
        for filename in files:
            # print(filename)
            os.remove(os.path.join(root, filename))
