# -*- coding: utf-8 -*-
"""
Authors: Tim Hessels
         UNESCO-IHE 2019
Contact: t.hessels@unesco-ihe.org
Repository: https://github.com/wateraccounting/watools
Module: Collect/GPM
"""
import os
import sys

import calendar

from joblib import Parallel, delayed
import requests

import numpy as np
import pandas as pd

# IHEWAcollect Modules
try:
    from ..collect import \
        Extract_Data_gz, Open_tiff_array, Save_as_tiff, \
        Clip_Dataset_GDAL
    # from ..gis import GIS
    # from ..dtime import Dtime
    from ..util import Log
except ImportError:
    from IHEWAcollect.templates.collect import \
        Extract_Data_gz, Open_tiff_array, Save_as_tiff, \
        Clip_Dataset_GDAL
    # from IHEWAcollect.templates.gis import GIS
    # from IHEWAcollect.templates.dtime import Dtime
    from IHEWAcollect.templates.util import Log


__this = sys.modules[__name__]


def DownloadData(status, conf):
    """
    This function downloads TRMM daily or monthly data

    Args:
      status (dict): Status.
      conf (dict): Configuration.
    """
    # Check the latitude and longitude and otherwise set lat or lon on greatest extent
    __this.account = conf['account']
    __this.product = conf['product']
    __this.Log = Log(conf['log'])

    Waitbar = 0
    cores = 1

    bbox = conf['product']['bbox']
    Startdate = conf['product']['period']['s']
    Enddate = conf['product']['period']['e']

    TimeCase = conf['product']['resolution']
    TimeFreq = conf['product']['freq']
    latlim = conf['product']['data']['lat']
    lonlim = conf['product']['data']['lon']

    folder = conf['folder']

    if bbox['s'] < latlim['s'] or bbox['n'] > latlim['n']:
        bbox['s'] = np.max(bbox['s'], latlim['s'])
        bbox['n'] = np.min(bbox['n'], latlim['n'])
    if bbox['w'] < lonlim['w'] or bbox['e'] > lonlim['e']:
        bbox['w'] = np.max(bbox['w'], lonlim['w'])
        bbox['e'] = np.min(bbox['e'], lonlim['e'])

    latlim = [bbox['s'], bbox['n']]
    lonlim = [bbox['w'], bbox['e']]

    # Check variables
    if not Startdate:
        Startdate = pd.Timestamp(conf['product']['data']['time']['s'])
    if not Enddate:
        Enddate = pd.Timestamp('Now')
    Dates = pd.date_range(Startdate,  Enddate, freq=TimeFreq)

    # Define directory and create it if not exists
    output_folder = folder['l']

    # Create Waitbar
       # if Waitbar == 1:
    #     import watools.Functions.Start.WaitbarConsole as WaitbarConsole
    #     total_amount = len(Dates)
    #     amount = 0
    #     WaitbarConsole.printWaitBar(amount, total_amount, prefix = 'Progress:', suffix = 'Complete', length = 50)

    # Define IDs
    yID = np.int16(np.array([np.ceil((latlim[0] + 90)*10),
                                   np.floor((latlim[1] + 90)*10)]))
    xID = np.int16(np.array([np.floor((lonlim[0])*10),
                             np.ceil((lonlim[1])*10)]) + 1800)

    # Pass variables to parallel function and run
    args = [output_folder, TimeCase, xID, yID, lonlim, latlim]

    if not cores:
        for Date in Dates:
            RetrieveData(Date, args)
            # if Waitbar == 1:
            #     amount += 1
            #     WaitbarConsole.printWaitBar(amount, total_amount, prefix = 'Progress:', suffix = 'Complete', length = 50)
        results = True
    else:
        results = Parallel(n_jobs=cores)(delayed(RetrieveData)(Date, args)
                                         for Date in Dates)

    return results


def RetrieveData(Date, args):
    """
    This function retrieves TRMM data for a given date from the
    ftp://disc2.nascom.nasa.gov server.

    Keyword arguments:
    Date -- 'yyyy-mm-dd'
    args -- A list of parameters defined in the DownloadData function.
    """
    # Argument
    [output_folder, TimeCase, xID, yID, lonlim, latlim] = args

    year = Date.year
    month= Date.month
    day = Date.day

    username = __this.account['data']['username']
    password = __this.account['data']['password']
    URL = __this.product['url']

    # Create https
    if TimeCase == 'daily':
        URL = 'https://gpm1.gesdisc.eosdis.nasa.gov/opendap/GPM_L3/GPM_3IMERGDF.05/%d/%02d/3B-DAY.MS.MRG.3IMERG.%d%02d%02d-S000000-E235959.V05.nc4.ascii?precipitationCal[%d:1:%d][%d:1:%d]'  %(year, month, year, month, day, xID[0], xID[1]-1, yID[0], yID[1]-1)
        DirFile = os.path.join(output_folder, "P_TRMM3B42.V7_mm-day-1_daily_%d.%02d.%02d.tif" %(year, month, day))
        Scaling = 1

    if TimeCase == 'monthly':
        URL = 'https://gpm1.gesdisc.eosdis.nasa.gov/opendap/hyrax/GPM_L3/GPM_3IMERGM.05/%d/3B-MO.MS.MRG.3IMERG.%d%02d01-S000000-E235959.%02d.V05B.HDF5.ascii?precipitation[%d:1:%d][%d:1:%d]'  %(year, year, month, month, xID[0], xID[1]-1, yID[0], yID[1]-1)
        Scaling = calendar.monthrange(year,month)[1] * 24
        DirFile = os.path.join(output_folder, "P_GPM.IMERG_mm-month-1_monthly_%d.%02d.01.tif" %(year, month))

    if not os.path.isfile(DirFile):
        dataset = requests.get(URL, allow_redirects=False,stream = True)
        try:
            get_dataset = requests.get(dataset.headers['location'], auth = (username,password),stream = True)
        except:
            from requests.packages.urllib3.exceptions import InsecureRequestWarning
            requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
            get_dataset  = requests.get(dataset.headers['location'], auth = (username, password), verify = False)

        # download data (first save as text file)
        pathtext = os.path.join(output_folder,'temp.txt')
        z = open(pathtext,'wb')
        z.write(get_dataset.content)
        z.close()

        # Open text file and remove header and footer
        data_start = np.genfromtxt(pathtext, dtype=float, skip_header=1, delimiter=',')
        data = data_start[:,1:] * Scaling
        data[data < 0] = -9999
        data = data.transpose()
        data = np.flipud(data)

        # Delete .txt file
        os.remove(pathtext)

        # Make geotiff file
        geo = [lonlim[0], 0.1, 0, latlim[1], 0, -0.1]
        Save_as_tiff(name=DirFile, data=data, geo=geo, projection="WGS84")

    return True
