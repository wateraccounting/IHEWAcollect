# -*- coding: utf-8 -*-
"""
Authors: Tim Hessels and Gonzalo Espinoza
         UNESCO-IHE 2016
Contact: t.hessels@unesco-ihe.org
         g.espinoza@unesco-ihe.org
Repository: https://github.com/wateraccounting/watools
Module: Collect/CMRSET

Restrictions:
The data and this python file may not be distributed to others without
permission of the WA+ team due data restriction of the CMRSET developers.

Description:
This script collects CMRSET data from the UNESCO-IHE FTP server. The data has a
monthly temporal resolution and a spatial resolution of 0.01 degree. The
resulting tiff files are in the WGS84 projection.
The data is available between 2000-01-01 till 2012-12-31.

Example:
from watools.Collect import CMRSET
CMRSET.monthly(Dir='C:/Temp/', Startdate='2003-02-24', Enddate='2003-03-09',
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
    This scripts downloads CMRSET ET data from the UNESCO-IHE ftp server.
    The output files display the total ET in mm for a period of one month.
    The name of the file corresponds to the first day of the month.

    Args:
      status (dict): Status.
      conf (dict): Configuration.
    """
    # Check the latitude and longitude and otherwise set lat or lon on greatest extent
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

    # Define directory and create it if not exists
    output_folder = folder['l']

    # Create Waitbar
    # if Waitbar == 1:
    #     import watools.Functions.Start.WaitbarConsole as WaitbarConsole
    #     total_amount = len(Dates)
    #     amount = 0
    #     WaitbarConsole.printWaitBar(amount, total_amount, prefix = 'Progress:', suffix = 'Complete', length = 50)

    for Date in Dates:

        # Date as printed in filename
        Filename_out = os.path.join(output_folder,
                                    __this.product['data']['fname']['l'].format(
                                        dtime=Date))

        # Define end filename
        Filename_in = __this.product['data']['fname']['r'].format(dtime=Date)

        # Temporary filename for the downloaded global file
        local_filename = os.path.join(output_folder, Filename_in)

        # Download the data from FTP server if the file not exists
        if not os.path.exists(Filename_out):
            try:
                Download_CMRSET_from_WA_FTP(local_filename, Filename_in)
            except BaseException as err:
                msg = "\nWas not able to download file with date %s" % Date
                print('{}\n{}'.format(msg, str(err)))
                __this.Log.write(datetime.datetime.now(),
                                 msg='{}\n{}'.format(msg, str(err)))
            else:
                # Clip dataset
                Clip_Dataset_GDAL(local_filename, Filename_out, latlim, lonlim)

                # delete old file
                os.remove(local_filename)

        # Adjust waitbar
        # if Waitbar == 1:
        #     amount += 1
        #     WaitbarConsole.printWaitBar(amount, total_amount, prefix = 'Progress:', suffix = 'Complete', length = 50)

    return


def Download_CMRSET_from_WA_FTP(local_filename, Filename_in):
    """
    This function retrieves CMRSET data for a given date from the
    ftp.wateraccounting.unesco-ihe.org server.

    Restrictions:
    The data and this python file may not be distributed to others without
    permission of the WA+ team due data restriction of the CMRSET developers.

    Keyword arguments:
     local_filename -- name of the temporary file which contains global CMRSET data
    Filename_in -- name of the end file with the monthly CMRSET data
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
    ftp.retrbinary("RETR " + Filename_in, lf.write)
    lf.close()

    return
