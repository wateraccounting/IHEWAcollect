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
