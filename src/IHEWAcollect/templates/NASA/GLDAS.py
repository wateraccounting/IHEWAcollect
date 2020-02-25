# -*- coding: utf-8 -*-
"""
**GLDAS Module**

"""
# General modules
import os
import sys
import datetime

import requests
# from requests.auth import HTTPBasicAuth => .netrc
from joblib import Parallel, delayed

import numpy as np
import pandas as pd
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
            date_e_doy = int(np.ceil(date_e.dayofyear / freq[0])) * int(freq[0]) + 1

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
    # if version == '2.1':
    #     zID = int(((Date - pd.Timestamp("2000-1-1")).days) * 8) + (period - 1) - 1
    # elif version == '2.0':
    #     zID = int(((Date - pd.Timestamp("1948-1-1")).days) * 8) + (period - 1) - 1

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
    # y_id = np.int16(np.array([
    #     np.floor((prod_lat_n - latlim[1]) / prod_lat_size),
    #     np.ceil((prod_lat_n - latlim[0]) / prod_lat_size)
    # ]))
    # x_id = np.int16(np.array([
    #     np.floor((lonlim[0] - prod_lon_w) / prod_lon_size),
    #     np.ceil((lonlim[1] - prod_lon_w) / prod_lon_size)
    # ]))

    # [w,s]--[e,s]
    #   |      |
    # [w,n]--[e,n]
    y_id = np.int16(np.array([
        np.floor((latlim[0] - prod_lat_s) / prod_lat_size),
        np.ceil((latlim[1] - prod_lat_s) / prod_lat_size)
    ]))
    x_id = np.int16(np.array([
        np.floor((lonlim[0] - prod_lon_w) / prod_lon_size),
        np.ceil((lonlim[1] - prod_lon_w) / prod_lon_size)
    ]))

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

        # ------------- #
        # Download data #
        # ------------- #
        if is_download:
            # https://disc.gsfc.nasa.gov/data-access#python
            # C:\Users\qpa001\.netrc
            file_conn_auth = os.path.join(os.path.expanduser("~"), ".netrc")
            with open(file_conn_auth, 'w+') as fp:
                fp.write('machine {m} login {u} password {p}\n'.format(
                    m='urs.earthdata.nasa.gov',
                    u=username,
                    p=password
                ))

            url = '{sr}{dr}{fl}'.format(sr=url_server,
                                        dr=url_dir,
                                        fl=remote_fname)
            # print('url: "{f}"'.format(f=url))

            try:
                # Connect to server
                conn = requests.get(url)
                # conn.raise_for_status()
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
    print('\33[94m{}\33[0m'.format(msg))
    __this.Log.write(datetime.datetime.now(), msg=msg)

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
    data_tmp = data_raw[date_id, y_id[0]: y_id[1], x_id[0]: x_id[1]]
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
    data = np.flipud(data)

    # [w,n]--[w,s]
    #   |      |
    # [e,n]--[e,s]
    # data = np.transpose(a=data, axes=(1, 0))

    # [w,s]--[w,n]
    #   |      |
    # [e,s]--[e,n]
    # data = np.rot90(data, k=1, axes=(0, 1))

    # close file
    fh.close()

    # ------- #
    # Convert #
    # ------- #
    # scale, units
    data[data == data_raw_missing] = np.nan
    data = data * data_raw_scale * data_multiplier

    # novalue data
    data[data == np.nan] = data_ndv

    # ------------ #
    # Saveas GTiff #
    # ------------ #
    geo = [lonlim[0], pixel_size, 0, latlim[1], 0, -pixel_size]
    Save_as_tiff(name=local_file, data=data, geo=geo, projection="WGS84")

    status_cod = 0
    return status_cod


class VariablesInfo:
    """
    This class contains the information about the GLDAS variables
    """
    # # Load factors / unit / type of variables / accounts
    # var_info = VariablesInfo(product['resolution'])
    # var_name = var_info.names[product['data']['variable']]
    # var_mult = var_info.factors[product['data']['variable']]
    # var_unit = var_info.units[product['data']['variable']]

    names = {'avgsurft_tavg': 'SurfaceTemperature',
             'canopint_tavg': 'TotCanopyWaterStorage',
             'Evap_tavg': 'ET',
             'lwdown_f_tavg': 'LWdown',
             'lwnet_tavg': 'LWnet',
             'psurf_f_tavg': 'P',
             'qair_f_tavg': 'Hum',
             'qg_tavg': 'G',
             'qh_tavg': 'H',
             'qle_tavg': 'LE',
             'qs_tavg': 'Rsur',
             'qsb_tavg': 'Rsubsur',
             'qsm_tavg': 'SnowMelt',
             'rainf_f_tavg': 'P',
             'swe_tavg': 'SnowWaterEquivalent',
             'swdown_f_tavg': 'SWdown',
             'swnet_tavg': 'SWnet',
             'snowf_tavg': 'Snow',
             'soilmoist_s_tav': 'SoilMoisturSurface',
             'soilmoist_rz_ta': 'SoilMoistureRootZone',
             'soilmoist_p_tav': 'SoilMoistureProfile',
             'tair_f_tavg': 'Tair',
             'wind_f_tavg': 'W',
             'tveg_tavg': 'Transpiration',
             'avgsurft': 'SurfaceTemperature',
             'canopint': 'TotCanopyWaterStorage',
             'evap': 'ET',
             'lwdown': 'LWdown',
             'lwnet': 'LWnet',
             'psurf': 'P',
             'qair': 'Hum',
             'qg': 'G',
             'qh': 'H',
             'qle': 'LE',
             'qs': 'Rsur',
             'qsb': 'Rsubsur',
             'qsm': 'SnowMelt',
             'rainf': 'P',
             'swe': 'SnowWaterEquivalent',
             'swdown': 'SWdown',
             'swnet': 'SWnet',
             'snowf': 'Snow',
             'tair': 'Tair',
             'wind': 'W'}
    descriptions = {'avgsurft_tavg': 'surface average surface temperature [k]',
                    'canopint_tavg': 'surface plant canopy surface water [kg/m^2]',
                    'Evap_tavg': 'surface total evapotranspiration [kg/m^2/s]',
                    'lwdown_f_tavg': 'surface surface incident longwave radiation'
                                     ' [w/m^2]',
                    'lwnet_tavg': 'surface net longwave radiation [w/m^2]',
                    'psurf_f_tavg': 'surface surface pressure [kPa]',
                    'qair_f_tavg': 'surface near surface specific humidity [kg/kg]',
                    'qg_tavg': 'surface ground heat flux [w/m^2]',
                    'qh_tavg': 'surface sensible heat flux [w/m^2]',
                    'qle_tavg': 'surface latent heat flux [w/m^2]',
                    'qs_tavg': 'storm surface runoff [kg/m^2/s]',
                    'qsb_tavg': 'baseflow-groundwater runoff [kg/m^2/s]',
                    'qsm_tavg': 'surface snowmelt [kg/m^2/s]',
                    'rainf_f_tavg': 'surface rainfall rate [kg/m^2/s]',
                    'swe_tavg': 'surface snow water equivalent [kg/m^2]',
                    'swdown_f_tavg': 'surface surface incident shortwave radiation'
                                     ' [w/m^2]',
                    'swnet_tavg': 'surface net shortwave radiation [w/m^2]',
                    'snowf_tavg': 'surface snowfall rate [kg/m^2/s]',
                    'soilmoist_s_tav': 'surface soil moisture [kg/m^2]',
                    'soilmoist_rz_ta': 'root zone soil moisture [kg/m^2]',
                    'soilmoist_p_tav': 'profile soil moisture [kg/m^2]',
                    'tair_f_tavg': 'surface near surface air temperature [k]',
                    'wind_f_tavg': 'surface near surface wind speed [m/s]',
                    'tveg_tavg': 'transpiration [w/m^2]',
                    'avgsurft': 'surface average surface temperature [k]',
                    'canopint': 'surface plant canopy surface water [kg/m^2]',
                    'evap': 'surface total evapotranspiration [kg/m^2/s]',
                    'lwdown': 'surface surface incident longwave radiation'
                              ' [w/m^2]',
                    'lwnet': 'surface net longwave radiation [w/m^2]',
                    'psurf': 'surface surface pressure [kPa]',
                    'qair': 'surface near surface specific humidity [kg/kg]',
                    'qg': 'surface ground heat flux [w/m^2]',
                    'qh': 'surface sensible heat flux [w/m^2]',
                    'qle': 'surface latent heat flux [w/m^2]',
                    'qs': 'storm surface runoff [kg/m^2/s]',
                    'qsb': 'baseflow-groundwater runoff [kg/m^2/s]',
                    'qsm': 'surface snowmelt [kg/m^2/s]',
                    'rainf': 'surface rainfall rate [kg/m^2/s]',
                    'swe': 'surface snow water equivalent [kg/m^2]',
                    'swdown': 'surface surface incident shortwave radiation'
                              ' [w/m^2]',
                    'swnet': 'surface net shortwave radiation [w/m^2]',
                    'snowf': 'surface snowfall rate [kg/m^2/s]',
                    'tair': 'surface near surface air temperature [k]',
                    'wind': 'surface near surface wind speed [m/s]'}
    factors = {'avgsurft_tavg': -273.15,
               'canopint_tavg': 1,
               'Evap_tavg': 86400,
               'lwdown_f_tavg': 1,
               'lwnet_tavg': 1,
               'psurf_f_tavg': 0.001,
               'qair_f_tavg': 1,
               'qg_tavg': 1,
               'qh_tavg': 1,
               'qle_tavg': 1,
               'qs_tavg': 86400,
               'qsb_tavg': 86400,
               'qsm_tavg': 86400,
               'rainf_f_tavg': 86400,
               'swe_tavg': 1,
               'swdown_f_tavg': 1,
               'swnet_tavg': 1,
               'snowf_tavg': 1,
               'soilmoist_s_tav': 1,
               'soilmoist_rz_ta': 1,
               'soilmoist_p_tav': 1,
               'tair_f_tavg': -273.15,
               'wind_f_tavg': 0.75,
               'tveg_tavg': 1,
               'avgsurft': -273.15,
               'canopint': 1,
               'evap': 86400,
               'lwdown': 1,
               'lwnet': 1,
               'psurf': 0.001,
               'qair': 1,
               'qg': 1,
               'qh': 1,
               'qle': 1,
               'qs': 86400,
               'qsb': 86400,
               'qsm': 86400,
               'rainf': 86400,
               'swe': 1,
               'swdown': 1,
               'swnet': 1,
               'snowf': 1,
               'tair': -273.15,
               'wind': 1}
    types = {'avgsurft_tavg': 'state',
             'canopint_tavg': 'state',
             'Evap_tavg': 'flux',
             'lwdown_f_tavg': 'state',
             'lwnet_tavg': 'state',
             'psurf_f_tavg': 'state',
             'qair_f_tavg': 'state',
             'qg_tavg': 'state',
             'qh_tavg': 'state',
             'qle_tavg': 'state',
             'qs_tavg': 'flux',
             'qsb_tavg': 'flux',
             'qsm_tavg': 'flux',
             'rainf_f_tavg': 'flux',
             'swe_tavg': 'state',
             'swdown_f_tavg': 'state',
             'swnet_tavg': 'state',
             'snowf_tavg': 'state',
             'soilmoist_s_tav': 'state',
             'soilmoist_rz_ta': 'state',
             'soilmoist_p_tav': 'state',
             'tair_f_tavg': 'state',
             'wind_f_tavg': 'state',
             'tveg_tavg': 'state',
             'avgsurft': 'state',
             'canopint': 'state',
             'evap': 'flux',
             'lwdown': 'state',
             'lwnet': 'state',
             'psurf': 'state',
             'qair': 'state',
             'qg': 'state',
             'qh': 'state',
             'qle': 'state',
             'qs': 'flux',
             'qsb': 'flux',
             'qsm': 'flux',
             'rainf': 'flux',
             'swe': 'state',
             'swdown': 'state',
             'swnet': 'state',
             'snowf': 'state',
             'tair': 'state',
             'wind': 'state'}

    def __init__(self, step):
        if step == 'three_hourly':
            self.units = {'avgsurft': 'C',
                          'canopint': 'mm',
                          'Evap_tavg': 'mm-3H-1',
                          'lwdown': 'W-m-2',
                          'lwnet': 'W-m-2',
                          'psurf': 'kpa',
                          'qair': 'kg-kg',
                          'qg': 'W-m-2',
                          'qh': 'W-m-2',
                          'qle': 'W-m-2',
                          'qs': 'mm-3H-1',
                          'qsb': 'mm-3H-1',
                          'qsm': 'mm-3H-1',
                          'rainf': 'mm-3H-1',
                          'swe': 'mm',
                          'swdown': 'W-m-2',
                          'swnet': 'W-m-2',
                          'snowf': 'mm',
                          'tair': 'C',
                          'wind': 'm-s-1'}
        elif step == 'daily':
            self.units = {'avgsurft_tavg': 'C',
                          'canopint_tavg': 'mm',
                          'evap_tavg': 'mm-day-1',
                          'lwdown_f_tavg': 'W-m-2',
                          'lwnet_tavg': 'W-m-2',
                          'psurf_f_tavg': 'kpa',
                          'qair_f_tavg': 'kg-kg',
                          'qg_tavg': 'W-m-2',
                          'qh_tavg': 'W-m-2',
                          'qle_tavg': 'W-m-2',
                          'qs_tavg': 'mm-day-1',
                          'qsb_tavg': 'mm-day-1',
                          'qsm_tavg': 'mm-day-1',
                          'rainf_f_tavg': 'mm-day-1',
                          'swe_tavg': 'mm',
                          'swdown_f_tavg': 'W-m-2',
                          'swnet_tavg': 'W-m-2',
                          'snowf_tavg': 'mm',
                          'soilmoist_s_tav': 'kg-m-2',
                          'soilmoist_rz_ta': 'kg-m-2',
                          'soilmoist_p_tav': 'kg-m-2',
                          'tair_f_tavg': 'C',
                          'wind_f_tavg': 'm-s-1',
                          'tveg_tavg': 'W-m-2'}
        elif step == 'monthly':
            self.units = {'avgsurft_tavg': 'C',
                          'canopint_tavg': 'mm',
                          'Evap_tavg': 'mm-month-1',
                          'lwdown_f_tavg': 'W-m-2',
                          'lwnet_tavg': 'W-m-2',
                          'psurf_f_tavg': 'kpa',
                          'qair_f_tavg': 'kg-kg',
                          'qg_tavg': 'W-m-2',
                          'qh_tavg': 'W-m-2',
                          'qle_tavg': 'W-m-2',
                          'qs_tavg': 'mm-month-1',
                          'qsb_tavg': 'mm-month-1',
                          'qsm_tavg': 'mm-month-1',
                          'rainf_f_tavg': 'mm-month-1',
                          'swe_tavg': 'mm',
                          'swdown_f_tavg': 'W-m-2',
                          'swnet_tavg': 'W-m-2',
                          'snowf_tavg': 'mm',
                          'soilmoist_s_tav': 'kg-m-2',
                          'soilmoist_rz_ta': 'kg-m-2',
                          'soilmoist_p_tav': 'kg-m-2',
                          'tair_f_tavg': 'C',
                          'wind_f_tavg': 'm-s-1',
                          'tveg_tavg': 'W-m-2'}
        else:
            raise KeyError("The input time step is not supported")
