# -*- coding: utf-8 -*-

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
        Extract_Data_gz, Open_tiff_array, Save_as_tiff, \
        Clip_Dataset_GDAL
    from ..gis import GIS
    from ..dtime import Dtime
    from ..util import Log
except ImportError:
    from IHEWAcollect.templates.collect import \
        Extract_Data_gz, Open_tiff_array, Save_as_tiff, \
        Clip_Dataset_GDAL
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
    This function downloads GLDAS CLSM daily data

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
        date_s = pd.Timestamp('{} 03:00:00'.format(product['data']['time']['s']))
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
    # if version == '2.1':
    #     zID = int(((Date - pd.Timestamp("2000-1-1")).days) * 8) + (period - 1) - 1
    # elif version == '2.0':
    #     zID = int(((Date - pd.Timestamp("1948-1-1")).days) * 8) + (period - 1) - 1

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

    pixel_size = abs(product['data']['lat']['r'])
    pixel_w = int(product['data']['dem']['w'])
    pixel_h = int(product['data']['dem']['h'])

    data_ndv = product['nodata']
    data_type = product['data']['dtype']['l']
    data_multiplier = float(product['data']['units']['m'])
    data_variable = product['data']['variable']

    # Define arg_IDs
    prod_lat_s = product['data']['lat']['s']
    prod_lon_w = product['data']['lon']['w']
    prod_lat_size = abs(product['data']['lat']['r'])
    prod_lon_size = abs(product['data']['lon']['r'])

    # y_id = np.int16(np.array([
    #     pixel_h - np.ceil((latlim[1] + abs(prod_lat_s)) / prod_lat_size),
    #     pixel_h - np.floor((latlim[0] + abs(prod_lat_s)) / prod_lat_size)
    # ]))
    # x_id = np.int16(np.array([
    #     np.floor((lonlim[0] + abs(prod_lon_w)) / prod_lon_size),
    #     np.ceil((lonlim[1] + abs(prod_lon_w)) / prod_lon_size)
    # ]))
    y_id = np.int16(np.array([
        np.ceil((latlim[0] - prod_lat_s) / prod_lat_size),
        np.floor((latlim[1] - prod_lat_s) / prod_lat_size)
    ]))
    x_id = np.int16(np.array([
        np.ceil((lonlim[0] - prod_lon_w) / prod_lon_size),
        np.floor((lonlim[1] - prod_lon_w) / prod_lon_size)
    ]))

    return latlim, lonlim, date, \
           product, \
           username, password, apitoken, \
           url_server, url_dir, \
           fname_r, fname_t, fname_l, \
           file_r, file_t, file_l, \
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
        # https://disc.gsfc.nasa.gov/data-access#python
        # C:\Users\qpa001\.netrc
        file_conn_auth = os.path.join(os.path.expanduser("~"), ".netrc")
        with open(file_conn_auth, 'w+') as fp:
            fp.write('machine {m} login {u} password {p}\n'.format(
                m='urs.earthdata.nasa.gov',
                u=username,
                p=password
            ))

        url = '{sr}{dr}{fl}'.format(sr=url_server, dr=url_dir, fl=remote_fname)
        # print('url: "{f}"'.format(f=url))

        try:
            # Connect to server
            msg = 'Downloading "{f}"'.format(f=remote_fname)
            print('{}'.format(msg))
            __this.Log.write(datetime.datetime.now(), msg=msg)

            conn = requests.get(url)
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
                    with open(remote_file, 'wb') as fp:
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

    # Load data from downloaded remote file
    fh = Dataset(remote_file, mode='r')

    data_raw = fh.variables[data_variable]
    if 'missing_value' in data_raw.ncattrs():
        data_raw_missing = data_raw.missing_value
    else:
        data_raw_missing = data_raw._FillValue
    if 'scale_factor' in data_raw.ncattrs():
        data_raw_scale = data_raw.scale_factor
    else:
        data_raw_scale = 1.0

    # Generate temporary files

    # Clip data
    data_tmp = data_raw[:, y_id[0]: y_id[1], x_id[0]: x_id[1]]

    # data = np.squeeze(data_tmp.data, axis=0)
    data = np.flipud(np.squeeze(data_tmp.data, axis=0))
    # data = np.swapaxes(data_tmp, 0, 1)
    fh.close()

    # Convert units, set NVD
    data[data == data_raw_missing] = np.nan
    data = data * data_raw_scale * data_multiplier

    data[data == np.nan] = data_ndv

    # save as GTiff
    geo = [lonlim[0], pixel_size, 0, latlim[1], 0, -pixel_size]
    Save_as_tiff(name=local_file, data=data, geo=geo, projection="WGS84")

    status = 0
    return status


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
