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



