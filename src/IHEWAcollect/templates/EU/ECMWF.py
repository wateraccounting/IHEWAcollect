# -*- coding: utf-8 -*-
"""
**ECMWF Module**

https://confluence.ecmwf.int/display/WEBAPI/Access+ECMWF+Public+Datasets

$HOME/.ecmwfapirc
{
    "url"   : "https://api.ecmwf.int/v1",
    "key"   : "4fe81af725d8f7647e10d35cadf7825e",
    "email" : "quanpan302@hotmail.com"
}
"""
# General modules
import os
import sys
import datetime

from ecmwfapi import ECMWFDataServer

import numpy as np
import pandas as pd
from netCDF4 import Dataset

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

    account = conf['account']
    folder = conf['folder']
    product = conf['product']

    # Init supported classes
    __this.GIS = GIS(status, conf)
    __this.Dtime = Dtime(status, conf)
    __this.Log = Log(conf['log'])

    return account, folder, product


def DownloadData(Dir, Var, Startdate, Enddate, latlim, lonlim, Waitbar, cores,
                 TimeCase, CaseParameters):
    """This is main interface.

    Args:
        status (dict): Status.
        conf (dict): Configuration.
    """
    # Define local variable
    status_cod = -1
    # is_waitbar = False

    return status_cod


def download_product(latlim, lonlim, dates,
                     account, folder, product,
                     is_waitbar) -> int:
    # Define local variable
    status_cod = -1
    # total = len(dates)
    cores = 1

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


class VariablesInfo:
    """
    This class contains the information about the ECMWF variables
    http://rda.ucar.edu/cgi-bin/transform?xml=/metadata/ParameterTables/WMO_GRIB1.98-0.128.xml&view=gribdoc
    """
    number_para = {'T': 130,
                   '2T': 167,
                   'SRO': 8,
                   'SSRO': 9,
                   'WIND': 10,
                   '10SI': 207,
                   'SP': 134,
                   'Q': 133,
                   'SSR': 176,
                   'R': 157,
                   'E': 182,
                   'SUND': 189,
                   'RO': 205,
                   'TP': 228,
                   '10U': 165,
                   '10V': 166,
                   '2D': 168,
                   'SR': 173,
                   'AL': 174,
                   'HCC': 188}

    var_name = {'T': 't',
                '2T': 't2m',
                'SRO': 'sro',
                'SSRO': 'ssro',
                'WIND': 'wind',
                '10SI': '10si',
                'SP': 'sp',
                'Q': 'q',
                'SSR': 'ssr',
                'R': 'r',
                'E': 'e',
                'SUND': 'sund',
                'RO': 'ro',
                'TP': 'tp',
                '10U': 'u10',
                '10V': 'v10',
                '2D': 'd2m',
                'SR': 'sr',
                'AL': 'al',
                'HCC': 'hcc'}

    # ECMWF data
    descriptions = {'T': 'Temperature [K]',
                    '2T': '2 meter Temperature [K]',
                    'SRO': 'Surface Runoff [m]',
                    'SSRO': 'Sub-surface Runoff [m]',
                    'WIND': 'Wind speed [m s-1]',
                    '10SI': '10 metre windspeed [m s-1]',
                    'SP': 'Surface Pressure [pa]',
                    'Q': 'Specific humidity [kg kg-1]',
                    'SSR': 'Surface solar radiation [W m-2 s]',
                    'R': 'Relative humidity [%]',
                    'E': 'Evaporation [m of water]',
                    'SUND': 'Sunshine duration [s]',
                    'RO': 'Runoff [m]',
                    'TP': 'Total Precipitation [m]',
                    '10U': '10 metre U wind component [m s-1]',
                    '10V': '10 metre V wind component [m s-1]',
                    '2D': '2 metre dewpoint temperature [K]',
                    'SR': 'Surface roughness [m]',
                    'AL': 'Albedo []',
                    'HCC': 'High cloud cover []'}

    # Factor add to get output
    factors_add = {'T': -273.15,
                   '2T': -273.15,
                   'SRO': 0,
                   'SSRO': 0,
                   'WIND': 0,
                   '10SI': 0,
                   'SP': 0,
                   'Q': 0,
                   'SSR': 0,
                   'R': 0,
                   'E': 0,
                   'SUND': 0,
                   'RO': 0,
                   'TP': 0,
                   '10U': 0,
                   '10V': 0,
                   '2D': -273.15,
                   'SR': 0,
                   'AL': 0,
                   'HCC': 0}

    # Factor multiply to get output
    factors_mul = {'T': 1,
                   '2T': 1,
                   'SRO': 1000,
                   'SSRO': 1000,
                   'WIND': 1,
                   '10SI': 1,
                   'SP': 0.001,
                   'Q': 1,
                   'SSR': 1,
                   'R': 1,
                   'E': 1000,
                   'SUND': 1,
                   'RO': 1000,
                   'TP': 1000,
                   '10U': 1,
                   '10V': 1,
                   '2D': 1,
                   'SR': 1,
                   'AL': 1,
                   'HCC': 1}

    types = {'T': 'state',
             '2T': 'state',
             'SRO': 'flux',
             'SSRO': 'flux',
             'WIND': 'state',
             '10SI': 'state',
             'SP': 'state',
             'Q': 'state',
             'SSR': 'state',
             'R': 'state',
             'E': 'flux',
             'SUND': 'flux',
             'RO': 'flux',
             'TP': 'flux',
             '10U': 'state',
             '10V': 'state',
             '2D': 'state',
             'SR': 'state',
             'AL': 'state',
             'HCC': 'state'}

    file_name = {'T': 'Tair2m',
                 '2T': 'Tair',
                 'SRO': 'Surf_Runoff',
                 'SSRO': 'Subsurf_Runoff',
                 'WIND': 'Wind',
                 '10SI': 'Wind10m',
                 'SP': 'Psurf',
                 'Q': 'Qair',
                 'SSR': 'SWnet',
                 'R': 'RelQair',
                 'E': 'Evaporation',
                 'SUND': 'SunDur',
                 'RO': 'Runoff',
                 'TP': 'P',
                 '10U': 'Wind_U',
                 '10V': 'Wind_V',
                 '2D': 'Dewpoint2m',
                 'SR': 'SurfRoughness',
                 'AL': 'Albedo',
                 'HCC': 'HighCloudCover'
                 }

    DownloadType = {'T': 3,
                    '2T': 1,
                    'SRO': 0,
                    'SSRO': 0,
                    'WIND': 0,
                    '10SI': 0,
                    'SP': 1,
                    'Q': 3,
                    'SSR': 2,
                    'R': 3,
                    'E': 2,
                    'SUND': 2,
                    'RO': 2,
                    'TP': 2,
                    '10U': 1,
                    '10V': 1,
                    '2D': 1,
                    'SR': 1,
                    'AL': 1,
                    'HCC': 1
                    }

    def __init__(self, step):

        # output units after applying factor
        if step == 'six_hourly':
            self.units = {'T': 'C',
                          '2T': 'C',
                          'SRO': 'mm',
                          'SSRO': 'mm',
                          'WIND': 'm_s-1',
                          '10SI': 'm_s-1',
                          'SP': 'kpa',
                          'Q': 'kg_kg-1',
                          'SSR': 'W_m-2_s',
                          'R': 'percentage',
                          'E': 'mm',
                          'SUND': 's',
                          'RO': 'mm',
                          'TP': 'mm',
                          '10U': 'm_s-1',
                          '10V': 'm_s-1',
                          '2D': 'C',
                          'SR': 'm',
                          'AL': '-',
                          'HCC': '-'
                          }

        elif step == 'daily':
            self.units = {'T': 'C',
                          '2T': 'C',
                          'SRO': 'mm',
                          'SSRO': 'mm',
                          'WIND': 'm_s-1',
                          '10SI': 'm_s-1',
                          'SP': 'kpa',
                          'Q': 'kg_kg-1',
                          'SSR': 'W_m-2_s',
                          'R': 'percentage',
                          'E': 'mm',
                          'SUND': 's',
                          'RO': 'mm',
                          'TP': 'mm',
                          '10U': 'm_s-1',
                          '10V': 'm_s-1',
                          '2D': 'C',
                          'SR': 'm',
                          'AL': '-',
                          'HCC': '-'}

        elif step == 'monthly':
            self.units = {'T': 'C',
                          '2T': 'C',
                          'SRO': 'mm',
                          'SSRO': 'mm',
                          'WIND': 'm_s-1',
                          '10SI': 'm_s-1',
                          'SP': 'kpa',
                          'Q': 'kg_kg-1',
                          'SSR': 'W_m-2_s',
                          'R': 'percentage',
                          'E': 'mm',
                          'SUND': 's',
                          'RO': 'mm',
                          'TP': 'mm',
                          '10U': 'm_s-1',
                          '10V': 'm_s-1',
                          '2D': 'C',
                          'SR': 'm',
                          'AL': '-',
                          'HCC': '-'}

        else:
            raise KeyError("The input time step is not supported")
