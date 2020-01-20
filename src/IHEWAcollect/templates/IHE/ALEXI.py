# -*- coding: utf-8 -*-
"""
**ALEXI**

`Restrictions`

The data and this python file may not be distributed to others without
permission of the WA+ team.

`Description`

This module downloads ALEXI data from
``ftp.wateraccounting.unesco-ihe.org``.

Use the ALEXI.daily function to download
and create weekly ALEXI images in Gtiff format.

The data is available between ``2003-01-01 till 2015-12-31``.

The output file with the name ``2003.01.01`` contains
the **total evaporation** in ``mm`` for the period of ``1 January - 7 January``.

**Examples:**
::

    from IHEWAcollect import ALEXI
    ALEXI.daily(Dir='C:/Temp/',
                Startdate='2003-12-01', Enddate='2004-01-20',
                latlim=[-10, 30], lonlim=[-20, -10])
"""
# General modules
import os
import sys
import glob
# import shutil

import math
import datetime

from urllib.parse import urlparse
from ftplib import FTP

import numpy as np
import pandas as pd

# from netCDF4 import Dataset

# IHEWAcollect Modules
try:
    from ..collect import \
        Extract_Data_gz, Open_tiff_array, Save_as_tiff
    # from ..gis import GIS
    # from ..dtime import Dtime
    from ..util import Log
except ImportError:
    from src.IHEWAcollect.templates.collect import \
        Extract_Data_gz, Open_tiff_array, Save_as_tiff
    # from src.IHEWAcollect.templates.gis import GIS
    # from src.IHEWAcollect.templates.dtime import Dtime
    from src.IHEWAcollect.templates.util import Log


__this = sys.modules[__name__]


def DownloadData(status, conf):
    """Downloads ALEXI ET data

    This scripts downloads ALEXI ET data from the UNESCO-IHE ftp server.
    The output files display the total ET in mm for a period of one week.
    The name of the file corresponds to the first day of the week.

    Args:
      status (dict): Status.
      conf (dict): Configuration.

    Returns:
      str: TimeStep, 'daily' or 'weekly'.
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

    # Make a panda timestamp of the date
    try:
        Enddate = pd.Timestamp(Enddate)
    except BaseException:
        Enddate = Enddate

    if TimeStep == 'weekly':

        # Define the Startdate of ALEXI
        DOY = datetime.datetime.strptime(Startdate,
                                         '%Y-%m-%d').timetuple().tm_yday
        Year = datetime.datetime.strptime(Startdate,
                                          '%Y-%m-%d').timetuple().tm_year

        # Change the startdate so it includes an ALEXI date
        DOYstart = int(math.ceil(DOY / 7.0) * 7 + 1)
        DOYstart = str('%s-%s' % (DOYstart, Year))
        Day = datetime.datetime.strptime(DOYstart, '%j-%Y')
        Month = '%02d' % Day.month
        Day = '%02d' % Day.day
        Date = (str(Year) + '-' + str(Month) + '-' + str(Day))
        DOY = datetime.datetime.strptime(Date,
                                         '%Y-%m-%d').timetuple().tm_yday
        # The new Startdate
        Date = pd.Timestamp(Date)

        # amount of Dates weekly
        Dates = pd.date_range(Date, Enddate, freq=freq)

    if TimeStep == 'daily':
        # Define Dates
        Dates = pd.date_range(Startdate, Enddate, freq=freq)

    total_amount = len(Dates)
    # Create Waitbar
    # if Waitbar == 1:
    #     amount = 0
    #     collect.WaitBar(amount, total_amount,
    #                     prefix='ALEXI:', suffix='Complete',
    #                     length=50)

    if TimeStep == 'weekly':
        ALEXI_weekly(Date, Enddate,
                     folder['l'],
                     latlim, lonlim,
                     Year,
                     Waitbar,
                     total_amount, TimeStep)
        return 'weekly'

    if TimeStep == 'daily':
        ALEXI_daily(Dates,
                    folder['l'],
                    latlim, lonlim,
                    Waitbar,
                    total_amount, TimeStep)
        return 'daily'


def Download_ALEXI_from_WA_FTP(local_filename, DirFile, filename,
                               lonlim, latlim, yID, xID, TimeStep):
    """Retrieves ALEXI data

    This function retrieves ALEXI data for a given date from the
    `<ftp.wateraccounting.unesco-ihe.org>`_ server.

    Args:
      local_filename (str): name of the temporary file which contains global ALEXI data.
      DirFile (str): name of the end file with the weekly ALEXI data.
      filename (str): name of the end file.
      latlim (list): [ymin, ymax] (values must be between -60 and 70).
      lonlim (list): [xmin, xmax] (values must be between -180 and 180).
      yID (list): latlim to index.
      xID (list): lonlim to index.
      TimeStep (str): 'daily' or 'weekly'  (by using here monthly,
        an older dataset will be used).
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
    ftp = FTP(ftpserver)
    ftp.login(username, password)
    ftp.cwd(directory)
    lf = open(local_filename, "wb")
    ftp.retrbinary("RETR " + filename, lf.write)
    lf.close()

    if TimeStep == "daily":
        Extract_Data_gz(local_filename, os.path.splitext(local_filename)[0])

        raw_data = np.fromfile(os.path.splitext(local_filename)[0], dtype="<f4")
        dataset = np.flipud(np.resize(raw_data, [3000, 7200]))
        # Values are in MJ/m2d so convert to mm/d
        data = dataset[yID[0]:yID[1], xID[0]:xID[1]] / 2.45  # mm/d
        data[data < 0] = -9999

    if TimeStep == "weekly":
        # Open global ALEXI data
        dataset = Open_tiff_array(local_filename)

        # Clip extend out of world data
        data = dataset[yID[0]:yID[1], xID[0]:xID[1]]
        data[data < 0] = -9999

    # make geotiff file
    geo = [lonlim[0], 0.05, 0, latlim[1], 0, -0.05]
    Save_as_tiff(name=DirFile, data=data, geo=geo, projection="WGS84")

    return


def ALEXI_daily(Dates, output_folder, latlim, lonlim, Waitbar, total_amount, TimeStep):
    amount = 0
    for Date in Dates:

        # Date as printed in filename
        DirFile = os.path.join(output_folder,
                               __this.product['data']['fname']['l'].format(dtime=Date))
        DOY = Date.timetuple().tm_yday

        # Define end filename
        filename = "EDAY_CERES_%d%03d.dat.gz" % (Date.year, DOY)

        # Temporary filename for the downloaded global file
        local_filename = os.path.join(output_folder, filename)

        # Define IDs
        yID = 3000 - np.int16(
            np.array([np.ceil((latlim[1] + 60) * 20), np.floor((latlim[0] + 60) * 20)]))
        xID = np.int16(
            np.array([np.floor((lonlim[0]) * 20), np.ceil((lonlim[1]) * 20)]) + 3600)

        # Download the data from FTP server if the file not exists
        if not os.path.exists(DirFile):
            try:
                Download_ALEXI_from_WA_FTP(local_filename, DirFile, filename, lonlim,
                                           latlim, yID, xID, TimeStep)
            except BaseException:
                msg = "\nWas not able to download file with date %s" % Date
                print(msg)
                __this.Log.write(datetime.datetime.now(), msg=msg)

        # # Adjust waitbar
        # if Waitbar == 1:
        #     amount += 1
        #     collect.WaitBar(amount, total_amount,
        #                     prefix='ALEXI:', suffix='Complete',
        #                     length=50)

        os.remove(local_filename)
        os.remove(os.path.splitext(local_filename)[0])

    # os.chdir(output_folder)
    # re = glob.glob("*.dat")
    # for f in re:
    #     os.remove(os.path.join(output_folder, f))


def ALEXI_weekly(Date, Enddate, output_folder, latlim, lonlim, Year, Waitbar,
                 total_amount, TimeStep):
    # Define the stop conditions
    Stop = Enddate.toordinal()
    End_date = 0
    amount = 0
    while End_date == 0:

        # Date as printed in filename
        Datesname = Date + pd.DateOffset(days=-7)
        DirFile = os.path.join(output_folder,
                               __this.product['data']['fname']['l'].format(dtime=Date))

        # Define end filename
        filename = "ALEXI_weekly_mm_%s_%s.tif" % (
            Date.strftime('%j'), Date.strftime('%Y'))

        # Temporary filename for the downloaded global file
        local_filename = os.path.join(output_folder, filename)

        # Create the new date for the next download
        Datename = (str(Date.strftime('%Y')) + '-' + str(
            Date.strftime('%m')) + '-' + str(Date.strftime('%d')))

        # Define IDs
        yID = 3000 - np.int16(
            np.array([np.ceil((latlim[1] + 60) * 20), np.floor((latlim[0] + 60) * 20)]))
        xID = np.int16(
            np.array([np.floor((lonlim[0]) * 20), np.ceil((lonlim[1]) * 20)]) + 3600)

        # Download the data from FTP server if the file not exists
        if not os.path.exists(DirFile):
            try:
                Download_ALEXI_from_WA_FTP(local_filename, DirFile, filename, lonlim,
                                           latlim, yID, xID, TimeStep)
            except BaseException:
                msg = "\nWas not able to download file with date %s" % Date
                print('{}\n{}'.format(msg, str(err)))
                __this.Log.write(datetime.datetime.now(), msg='{}\n{}'.format(msg, str(err)))

        # Current DOY
        DOY = datetime.datetime.strptime(Datename,
                                         '%Y-%m-%d').timetuple().tm_yday

        # Define next day
        DOY_next = int(DOY + 7)
        if DOY_next >= 366:
            DOY_next = 8
            Year += 1
        DOYnext = str('%s-%s' % (DOY_next, Year))
        DayNext = datetime.datetime.strptime(DOYnext, '%j-%Y')
        Month = '%02d' % DayNext.month
        Day = '%02d' % DayNext.day
        Date = (str(Year) + '-' + str(Month) + '-' + str(Day))

        # # Adjust waitbar
        # if Waitbar == 1:
        #     amount += 1
        #     collect.WaitBar(amount, total_amount,
        #                     prefix='ALEXI:', suffix='Complete',
        #                     length=50)

        # Check if this file must be downloaded
        Date = pd.Timestamp(Date)
        if Date.toordinal() > Stop:
            End_date = 1

        os.remove(local_filename)
