# -*- coding: utf-8 -*-
"""
Authors: Tim Hessels and Gonzalo Espinoza
         UNESCO-IHE 2016
Contact: t.hessels@unesco-ihe.org
         g.espinoza@unesco-ihe.org
Repository: https://github.com/wateraccounting/watools
Module: Collect/ETmonitor

Restrictions:
The data and this python file may not be distributed to others without
permission of the WA+ team due data restriction of the ETmonitor developers.

Description:
This script collects ETmonitor data from the UNESCO-IHE FTP server. The data has a
monthly temporal resolution and a spatial resolution of 0.01 degree. The
resulting tiff files are in the WGS84 projection.
The data is available between 2008-01-01 till 2013-12-31.

Example:
from watools.Collect import ETmonitor
ETmonitor.ET_monthly(Dir='C:/Temp/', Startdate='2003-02-24', Enddate='2003-03-09',
                     latlim=[50,54], lonlim=[3,7])

"""
# General modules
import os
import sys

import datetime

from urllib.parse import urlparse
from ftplib import FTP

import numpy as np
import pandas as pd

# IHEWAcollect Modules
try:
    from ..collect import \
        Extract_Data_gz, Open_tiff_array, Save_as_tiff, \
        reproject_MODIS, Clip_Dataset_GDAL
    # from ..gis import GIS
    # from ..dtime import Dtime
    from ..util import Log
except ImportError:
    from src.IHEWAcollect.templates.collect import \
        Extract_Data_gz, Open_tiff_array, Save_as_tiff, \
        reproject_MODIS, Clip_Dataset_GDAL
    # from src.IHEWAcollect.templates.gis import GIS
    # from src.IHEWAcollect.templates.dtime import Dtime
    from src.IHEWAcollect.templates.util import Log


__this = sys.modules[__name__]


def DownloadData(status, conf):
    """
    This scripts downloads ETmonitor ET data from the UNESCO-IHE ftp server.
    The output files display the total ET in mm for a period of one month.
    The name of the file corresponds to the first day of the month.

    Args:
      status (dict): Status.
      conf (dict): Configuration.
    """
    __this.account = conf['account']
    __this.product = conf['product']
    __this.Log = Log(conf['log'])

    Waitbar = 0

    bbox = conf['product']['bbox']
    Startdate = conf['product']['period']['s']
    Enddate = conf['product']['period']['e']

    TimeStep = conf['product']['resolution']
    freq = conf['product']['freq']
    latlim = conf['product']['data']['lat']
    lonlim = conf['product']['data']['lon']

    folder = conf['folder']

    # Check the latitude and longitude and otherwise set lat or lon on greatest extent
    if bbox['s'] < latlim['s'] or bbox['n'] > latlim['n']:
        bbox['s'] = np.max(bbox['s'], latlim['s'])
        bbox['n'] = np.min(bbox['n'], latlim['n'])
    if bbox['w'] < lonlim['w'] or bbox['e'] > lonlim['e']:
        bbox['w'] = np.max(bbox['w'], lonlim['w'])
        bbox['e'] = np.min(bbox['e'], lonlim['e'])

    latlim = [bbox['s'], bbox['n']]
    lonlim = [bbox['w'], bbox['e']]

    # Check Startdate and Enddate
    if not Startdate:
        Startdate = pd.Timestamp(conf['product']['data']['time']['s'])
    if not Enddate:
        Enddate = pd.Timestamp(conf['product']['data']['time']['e'])

    # Creates dates library
    Dates = pd.date_range(Startdate, Enddate, freq=freq)

    # Create Waitbar
    # if Waitbar == 1:
    #     import watools.Functions.Start.WaitbarConsole as WaitbarConsole
    #     total_amount = len(Dates)
    #     amount = 0
    #     WaitbarConsole.printWaitBar(amount, total_amount, prefix = 'Progress:', suffix = 'Complete', length = 50)

    # Define directory and create it if not exists
    output_folder = folder['l']

    for Date in Dates:

        # Define year and month
        year = Date.year
        month = Date.month

        # Define end filename and Date as printed in filename
        Filename_in = __this.product['data']['fname']['r'].format(dtime=Date)
        Filename_out = os.path.join(output_folder,
                                    __this.product['data']['fname']['l'].format(dtime=Date))

        # Temporary filename for the downloaded global file
        local_filename = os.path.join(output_folder, Filename_in)

        # Download the data from FTP server if the file not exists
        if not os.path.exists(Filename_out):
            try:
                Download_ETmonitor_from_WA_FTP(local_filename, Filename_in)
            except BaseException as err:
                msg = "\nWas not able to download file with date %s" % Date
                print('{}\n{}'.format(msg, str(err)))
                __this.Log.write(datetime.datetime.now(), msg='{}\n{}'.format(msg, str(err)))
            else:
                # Reproject dataset
                epsg_to ='4326'
                name_reprojected_ETmonitor = reproject_MODIS(local_filename, epsg_to)

                # Clip dataset
                Clip_Dataset_GDAL(name_reprojected_ETmonitor, Filename_out, latlim, lonlim)
                os.remove(name_reprojected_ETmonitor)
                os.remove(local_filename)


        # Adjust waitbar
        # if Waitbar == 1:
        #     amount += 1
        #     WaitbarConsole.printWaitBar(amount, total_amount, prefix = 'Progress:', suffix = 'Complete', length = 50)

    return


def Download_ETmonitor_from_WA_FTP(local_filename, Filename_in):
    """
    This function retrieves ETmonitor data for a given date from the
    ftp.wateraccounting.unesco-ihe.org server.

    Restrictions:
    The data and this python file may not be distributed to others without
    permission of the WA+ team due data restriction of the ETmonitor developers.

    Keyword arguments:
     local_filename -- name of the temporary file which contains global ETmonitor data
    Filename_in -- name of the end file with the weekly ETmonitor data
     Type = Type of data ("act" or "pot")
    """

    # Collect account and FTP information
    username = __this.account['data']['username']
    password = __this.account['data']['password']

    ftpserver = urlparse(__this.product['url']).netloc
    directory = __this.product['data']['dir']

    fname = os.path.split(local_filename)[-1]
    msg = 'Downloading "{f}"'.format(f=fname)
    print('Downloading {f}'.format(f=fname))
    __this.Log.write(datetime.datetime.now(), msg=msg)

    # Download data from FTP
    ftp=FTP(ftpserver)
    ftp.login(username,password)
    ftp.cwd(directory)
    lf = open(local_filename, "wb")
    ftp.retrbinary("RETR " + Filename_in, lf.write)
    lf.close()

    return
