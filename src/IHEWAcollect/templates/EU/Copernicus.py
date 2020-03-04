# -*- coding: utf-8 -*-
"""
**Copernicus Module**

https://cds.climate.copernicus.eu/api-how-to

$HOME/.cdsapirc
url: https://cds.climate.copernicus.eu/api/v2
key: 17821:5e791c0b-9c10-4167-b849-402b0947aea9
"""
# General modules
import os
import sys
import datetime

import cdsapi

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
    This class contains the information about the Copernicus variables
    """
    number_para = {'T': 130}

    var_name = {'T': 't'}

    descriptions = {'T': 'Temperature [K]'}

    # Factor add to get output
    factors_add = {'T': -273.15}

    # Factor multiply to get output
    factors_mul = {'T': 1}

    types = {'T': 'state'}

    file_name = {'T': 'Tair2m'}

    DownloadType = {'T': 3}

    def __init__(self, step):
        if step == 'six_hourly':
            self.units = {'T': 'C'}
        elif step == 'daily':
            self.units = {'T': 'C'}
        elif step == 'monthly':
            self.units = {'T': 'C'}
        else:
            raise KeyError("The input time step is not supported")



