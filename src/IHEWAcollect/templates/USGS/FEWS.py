# -*- coding: utf-8 -*-
"""
Authors: Tim Hessels and Gonzalo Espinoza
         UNESCO-IHE 2016
Contact: t.hessels@unesco-ihe.org
         g.espinoza@unesco-ihe.org
Repository: https://github.com/wateraccounting/watools
Module: Collect/SSEBop

Restrictions:
The data and this python file may not be distributed to others without
permission of the WA+ team due data restriction of the SSEBop developers.

Description:
This script collects SSEBop data from the UNESCO-IHE FTP server or from the web. The data has a
monthly temporal resolution and a spatial resolution of 0.01 degree. The
resulting tiff files are in the WGS84 projection.
The data is available between 2003-01-01 till present.

Example:
from watools.Collect import SSEBop
SSEBop.monthly(Dir='C:/Temp/', Startdate='2003-02-24', Enddate='2003-03-09',
                     latlim=[50,54], lonlim=[3,7])

"""
# General modules
import os
import sys

import datetime

if sys.version_info[0] == 3:
    import urllib.parse
if sys.version_info[0] == 2:
    import urllib

import numpy as np
import pandas as pd

# IHEWAcollect Modules
try:
    from ..collect import \
        Extract_Data_gz, Open_tiff_array, Save_as_tiff, \
        Open_bil_array, Save_as_MEM, clip_data, Extract_Data_tar_gz
    # from ..gis import GIS
    # from ..dtime import Dtime
    from ..util import Log
except ImportError:
    from IHEWAcollect.templates.collect import \
        Extract_Data_gz, Open_tiff_array, Save_as_tiff, \
        Open_bil_array, Save_as_MEM, clip_data, Extract_Data_tar_gz
    # from IHEWAcollect.templates.gis import GIS
    # from IHEWAcollect.templates.dtime import Dtime
    from IHEWAcollect.templates.util import Log


__this = sys.modules[__name__]


def DownloadData(status, conf):
    """
    This scripts downloads SSEBop ET data from the UNESCO-IHE ftp server.
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
    freq_use = conf['product']['freq']
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
        Enddate = pd.Timestamp(datetime.datetime.now())

    # Creates dates library
    Dates = pd.date_range(Startdate, Enddate, freq=freq_use)

    # Define directory and create it if not exists
    output_folder = folder['l']
    remote_folder = folder['r']
    temp_folder = folder['t']

    # Create Waitbar
    # if Waitbar == 1:
    #     import watools.Functions.Start.WaitbarConsole as WaitbarConsole
    #     total_amount = len(Dates)
    #     amount = 0
    #     WaitbarConsole.printWaitBar(amount, total_amount, prefix='Progress:',
    #                                 suffix='Complete', length=50)

    for Date in Dates:

        # Date as printed in filename
        Filename_out = os.path.join(output_folder,
                                    __this.product['data']['fname']['l'].format(dtime=Date))

        # Define end filename
        Filename_in = __this.product['data']['fname']['r'].format(dtime=Date)
        Filename_tmp = __this.product['data']['fname']['t'].format(dtime=Date)

        # Temporary filename for the downloaded global file
        local_filename = os.path.join(output_folder, Filename_in)
        temp_filename = os.path.join(temp_folder, Filename_tmp)

        # Download the data from FTP server if the file not exists
        if not os.path.exists(Filename_out):
            try:
                Download_SSEBop_from_Web(local_filename, Filename_in)
            except BaseException as err:
                msg = "\nWas not able to download file with date %s" % Date
                print('{}\n{}'.format(msg, str(err)))
                __this.Log.write(datetime.datetime.now(),
                                 msg='{}\n{}'.format(msg, str(err)))
            else:
                # unzip the file
                Extract_Data_tar_gz(local_filename, temp_folder)

                # Clip dataset
                Array_ETpot = Open_bil_array(temp_filename)
                Array_ETpot = Array_ETpot / 100
                Geo_out = tuple([-180.5, 1, 0, 90.5, 0, -1])
                dest = Save_as_MEM(Array_ETpot, Geo_out, "WGS84")
                data, Geo_out = clip_data(dest, latlim, lonlim)
                Save_as_tiff(Filename_out, data, Geo_out, "WGS84")

                # delete old tif file
                os.remove(local_filename)
                os.remove(temp_filename)

        # Adjust waitbar
        # if Waitbar == 1:
        #     amount += 1
        #     WaitbarConsole.printWaitBar(amount, total_amount, prefix='Progress:',
        #                                 suffix='Complete', length=50)

    return


def Download_SSEBop_from_Web(local_filename, Filename_in):
    """
    This function retrieves SSEBop data for a given date from the
    https://edcintl.cr.usgs.gov server.

    Keyword arguments:
     local_filename -- name of the temporary file which contains global SSEBop data
    Filename_dir -- name of the end directory to put in the extracted data
    """
    URL = '{}{}{}'.format(__this.product['url'],
                          __this.product['data']['dir'],
                          Filename_in)

    fname = os.path.split(local_filename)[-1]
    msg = 'Downloading "{f}"'.format(f=fname)
    print('Downloading {f}'.format(f=fname))
    __this.Log.write(datetime.datetime.now(), msg=msg)

    # Download the data
    if sys.version_info[0] == 2:
        urllib.urlretrieve(URL, local_filename)
    if sys.version_info[0] == 3:
        urllib.request.urlretrieve(URL, local_filename)

    return

