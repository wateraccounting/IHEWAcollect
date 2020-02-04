# -*- coding: utf-8 -*-
"""

"""
# General modules
import os
import sys
import datetime

import re
from bs4 import BeautifulSoup
import requests
# from requests.auth import HTTPBasicAuth => .netrc
from joblib import Parallel, delayed

import numpy as np
import pandas as pd
# from netCDF4 import Dataset

# IHEWAcollect Modules
try:
    from ..collect import \
        Extract_Data_gz, Open_tiff_array, Save_as_tiff, \
        Open_array_info, Clip_Data

    from ..gis import GIS
    from ..dtime import Dtime
    from ..util import Log
except ImportError:
    from IHEWAcollect.templates.collect import \
        Extract_Data_gz, Open_tiff_array, Save_as_tiff, \
        Open_array_info, Clip_Data

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
    This function downloads GLEAM ET data

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
        date_dates = pd.date_range(date_s, date_e)
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
    status = -1
    total = len(dates)
    cores = 1

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

    # [w,n]--[w,s]
    #   |      |
    # [e,n]--[e,s]
    # y_id = np.int16(np.array([
    #     np.floor((lonlim[0] - prod_lon_w) / prod_lon_size),
    #     np.ceil((lonlim[1] - prod_lon_w) / prod_lon_size)
    # ]))
    # x_id = np.int16(np.array([
    #     np.floor((prod_lat_n - latlim[1]) / prod_lat_size),
    #     np.ceil((prod_lat_n - latlim[0]) / prod_lat_size)
    # ]))

    # [w,s]--[w,n]
    #   |      |
    # [e,s]--[e,n]
    # y_id = np.int16(np.array([
    #     np.floor((lonlim[0] - prod_lon_w) / prod_lon_size),
    #     np.ceil((lonlim[1] - prod_lon_w) / prod_lon_size)
    # ]))
    # x_id = np.int16(np.array([
    #     np.floor((latlim[0] - prod_lat_s) / prod_lat_size),
    #     np.ceil((latlim[1] - prod_lat_s) / prod_lat_size)
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
        # remote_fname_latlon = remote_fname.format(dtime=date, lat=1, lon=1)
        remote_fnames, remote_files = start_download_tiles(date, url_server, url_dir,
                                                           latlim, lonlim,
                                                           remote_fname, remote_file)

        for ifile in range(len(remote_fnames)):
            # Download the data from server if the file not exists
            msg = 'Downloading "{f}"'.format(f=remote_fnames[ifile])
            print('{}'.format(msg))
            __this.Log.write(datetime.datetime.now(), msg=msg)

            is_download = True
            if os.path.exists(remote_files[ifile]):
                if np.ceil(os.stat(remote_files[ifile]).st_size / 1024) > 0:
                    is_download = False

                    msg = 'Exist "{f}"'.format(f=remote_files[ifile])
                    print('\33[93m{}\33[0m'.format(msg))
                    __this.Log.write(datetime.datetime.now(), msg=msg)

            # ------------- #
            # Download data #
            # ------------- #
            if is_download:
                url = '{sr}{dr}{fl}'.format(sr=url_server,
                                            dr=url_dir,
                                            fl=remote_fnames[ifile])
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
                        fn=remote_fnames[ifile])
                    print('\33[91m{}\n{}\33[0m'.format(msg, str(err)))
                    __this.Log.write(datetime.datetime.now(),
                                     msg='{}\n{}'.format(msg, str(err)))
                    remote_file_status += 1
                else:
                    # Fetch data
                    # conn.status_code == requests.codes.ok
                    with open(remote_files[ifile], 'wb') as fp:
                        fp.write(conn.content)
                        conn.close()
                        remote_file_status += 0
            else:
                remote_file_status += 0

        # ---------------- #
        # Download success #
        # ---------------- #
        if len(remote_fnames) > 0:
            if remote_file_status == 0:
                local_file_status += convert_data(args)
        else:
            msg = 'No tiles found!'
            print('{}'.format(msg))
            __this.Log.write(datetime.datetime.now(), msg=msg)

        # --------------- #
        # Download finish #
        # --------------- #
        # raw_data = None
        # dataset = None
        # data = None
    else:
        local_file_status = 0

    status = remote_file_status + local_file_status

    msg = 'Finish'
    __this.Log.write(datetime.datetime.now(), msg=msg)
    return status


def start_download_scan(url, fname_r, lat, lon) -> tuple:
    """Scan tile name
    """
    ctime = ''

    # Get files on FTP server
    conn = requests.get(url)

    # Sum all the files on the server
    soup = BeautifulSoup(conn.content, "lxml")
    for ele in soup.findAll('a', attrs={'href': re.compile('(?i)(hdf)$')}):
        print(lat, lon, ele)
        if '{lat}{lon}'.format(lat=lat, lon=lon) == ele['href'].split('.')[-4]:
            ctime = ele['href'].split('.')[-2]

    return ctime


def start_download_tiles(date, url_server, url_dir,
                         latlim, lonlim, fname_r, file_r) -> tuple:
    """Get tile name
    """
    url = '{sr}{dr}'.format(sr=url_server, dr=url_dir)
    # print('url: "{f}"'.format(f=url))

    latmin = int(np.floor((90.0 - latlim[1]) / 10.))
    latmax = int(np.floor((90.0 - latlim[0]) / 10.))
    lonmin = int(np.floor((180.0 + lonlim[0]) / 10.))
    lonmax = int(np.floor((180.0 + lonlim[1]) / 10.))

    lat_steps = range(latmin, latmax, 1)
    lon_steps = range(lonmin, lonmax, 1)
    # [8,9], [17, 18]

    # tile_txt_tmp = np.genfromtxt(
    #     os.path.join(os.path.dirname(os.path.abspath(__file__)),
    #                  'sn_gring_10deg.txt'),
    #     skip_header=7,
    #     skip_footer=1,
    #     usecols=(0, 1, 2, 3, 4, 5, 6, 7, 8, 9))
    # print(tile_txt_tmp)
    # tile_txt = tile_txt_tmp[tile_txt_tmp[:, 2] >= -900, :]
    #
    # # calculate min and max longitude and latitude
    # # lat down    lat up      lon left     lon right
    # tile_txt_ext = np.empty([len(tile_txt), 6])
    # tile_txt_ext[:, 0] = tile_txt[:, 0]
    # tile_txt_ext[:, 1] = tile_txt[:,1]
    # tile_txt_ext[:, 2] = np.minimum(tile_txt[:, 3], tile_txt[:, 9])
    # tile_txt_ext[:, 3] = np.maximum(tile_txt[:, 5], tile_txt[:, 7])
    # tile_txt_ext[:, 4] = np.minimum(tile_txt[:, 2], tile_txt[:, 4])
    # tile_txt_ext[:, 5] = np.maximum(tile_txt[:, 6], tile_txt[:, 8])
    #
    # # Define the upper left tile
    # latlim_tiles_ul_tmp = tile_txt_ext[
    #     np.logical_and(
    #         tile_txt_ext[:, 2] <= latlim[1],
    #         tile_txt_ext[:, 3] >= latlim[1])]
    # latlim_tiles_ul = latlim_tiles_ul_tmp[
    #     np.logical_and(
    #         latlim_tiles_ul_tmp[:, 4] <= lonlim[0],
    #         latlim_tiles_ul_tmp[:, 5] >= lonlim[0])]
    #
    # # Define the lower right tile
    # latlim_tiles_lr_tmp = tile_txt_ext[
    #     np.logical_and(
    #         tile_txt_ext[:, 2] <= latlim[0],
    #         tile_txt_ext[:, 3] >= latlim[0])]
    # latlim_tiles_lr = latlim_tiles_lr_tmp[
    #     np.logical_and(
    #         latlim_tiles_lr_tmp[:, 4] <= lonlim[1],
    #         latlim_tiles_lr_tmp[:, 5] >= lonlim[1])]
    #
    # # Define the total tile
    # tiles = np.vstack([latlim_tiles_ul, latlim_tiles_lr])
    #
    # # Find the minimum horizontal and vertical tile value and
    # # the maximum horizontal and vertical tile value
    # tile_v = [tiles[:, 0].min(), tiles[:, 0].max()]
    # tile_h = [tiles[:, 1].min(), tiles[:, 1].max()]
    # [8,9], [17, 18]

    fnames = []
    files = []
    for lon_step in lon_steps:
        string_long = 'h{:02d}'.format(lon_step)
        for lat_step in lat_steps:
            string_lat = 'v{:02d}'.format(lat_step)

            ctime = start_download_scan(url, fname_r,
                                        string_lat, string_long)

            if ctime != '':
                fnames.append(fname_r.format(dtime=date, ctime=ctime,
                                             lat=string_lat, lon=string_long))
                files.append(file_r.format(dtime=date, ctime=ctime,
                                           lat=string_lat, lon=string_long))

    return fnames, files


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

    # --------- #
    # Load data #
    # --------- #
    remote_fnames, remote_files = start_download_tiles(date, url_server, url_dir,
                                                       latlim, lonlim,
                                                       remote_fname, remote_file)

    data = np.zeros([int((latlim[1] - latlim[0]) / pixel_size),
                     int((lonlim[1] - lonlim[0]) / pixel_size)])

    for ifile in range(len(remote_fnames)):
        # From downloaded remote file
        geo_trans, geo_proj, size_x, size_y = Open_array_info(remote_files[ifile])
        lat_min_merge = np.maximum(latlim[0], geo_trans[3] + size_y * geo_trans[5])
        lat_max_merge = np.minimum(latlim[1], geo_trans[3])
        lon_min_merge = np.maximum(lonlim[0], geo_trans[0])
        lon_max_merge = np.minimum(lonlim[1], geo_trans[0] + size_x * geo_trans[1])

        lonmerge = [lon_min_merge, lon_max_merge]
        latmerge = [lat_min_merge, lat_max_merge]
        data_tmp, geo_one = Clip_Data(remote_files[ifile], latmerge, lonmerge)

        y_start = int((geo_one[3] - latlim[1]) / geo_one[5])
        y_end = int(y_start + np.shape(data_tmp)[0])
        x_start = int((geo_one[0] - lonlim[0]) / geo_one[1])
        x_end = int(x_start + np.shape(data_tmp)[1])

        data[y_start:y_end, x_start:x_end] = data_tmp

        # From generated temporary file
        # Generate temporary files

        # Convert meta data to float
        # if np.logical_or(isinstance(data_raw_missing, str),
        #                  isinstance(data_raw_scale, str)):
        #     data_raw_missing = float(data_raw_missing)
        #     data_raw_scale = float(data_raw_scale)

    # transfer matrix to GTiff matrix
    # [w,n]--[e,n]
    #   |      |
    # [w,s]--[e,s]
    data = np.asarray(data)

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
    # data = np.rot90(data, k=1, axes=(0, 1))

    # close file
    # fh.close()

    # ------- #
    # Convert #
    # ------- #
    # scale, units
    # data[data == data_raw_missing] = np.nan
    data = data * data_multiplier

    # novalue data
    # data[data == np.nan] = data_ndv

    # ------------ #
    # Saveas GTiff #
    # ------------ #
    geo = [lonlim[0], pixel_size, 0, latlim[1], 0, -pixel_size]
    Save_as_tiff(name=local_file, data=data, geo=geo, projection="WGS84")

    status = 0
    return status
