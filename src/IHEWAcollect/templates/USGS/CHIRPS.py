# -*- coding: utf-8 -*-
"""
Authors: Tim Hessels and Gonzalo Espinoza
         UNESCO-IHE 2016
Contact: t.hessels@unesco-ihe.org
         g.espinoza@unesco-ihe.org
Repository: https://github.com/wateraccounting/watools
Module: Collect/CHIRPS
"""

# import general python modules
import os
import sys

import datetime

from urllib.parse import urlparse
from ftplib import FTP
from joblib import Parallel, delayed

import numpy as np
import pandas as pd

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
    """
    This function downloads CHIRPS daily or monthly data

    Args:
      status (dict): Status.
      conf (dict): Configuration.
    """
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
    output_folder = folder['l']

    # make directory if it not exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # check time variables
    if not Startdate:
        Startdate = pd.Timestamp(conf['product']['data']['time']['s'])
    if not Enddate:
        Enddate = pd.Timestamp('Now')

    # Create days
    Dates = pd.date_range(Startdate, Enddate, freq=TimeFreq)

    # Create Waitbar
    # if Waitbar == 1:
    #     import watools.Functions.Start.WaitbarConsole as WaitbarConsole
    #     total_amount = len(Dates)
    #     amount = 0
    #     WaitbarConsole.printWaitBar(amount, total_amount, prefix = 'Progress:', suffix = 'Complete', length = 50)

    # Check space variables
    if bbox['s'] < latlim['s'] or bbox['n'] > latlim['n']:
        bbox['s'] = np.max(bbox['s'], latlim['s'])
        bbox['n'] = np.min(bbox['n'], latlim['n'])
    if bbox['w'] < lonlim['w'] or bbox['e'] > lonlim['e']:
        bbox['w'] = np.max(bbox['w'], lonlim['w'])
        bbox['e'] = np.min(bbox['e'], lonlim['e'])

    latlim = [bbox['s'], bbox['n']]
    lonlim = [bbox['w'], bbox['e']]

    # Define IDs
    yID = 2000 - np.int16(np.array([np.ceil((latlim[1] + 50)*20),
                                    np.floor((latlim[0] + 50)*20)]))
    xID = np.int16(np.array([np.floor((lonlim[0] + 180)*20),
                             np.ceil((lonlim[1] + 180)*20)]))

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
    This function retrieves CHIRPS data for a given date from the
    ftp://chg-ftpout.geog.ucsb.edu server.

    Keyword arguments:
    Date -- 'yyyy-mm-dd'
    args -- A list of parameters defined in the DownloadData function.
    """
    # Argument
    [output_folder, TimeCase, xID, yID, lonlim, latlim] = args

    # open ftp server
    ftpserver = urlparse(__this.product['url']).netloc
    ftp = FTP(ftpserver, "", "")
    ftp.login()

    # Define FTP path to directory
    pathFTP = __this.product['data']['dir'].format(dtime=Date)

    # find the document name in this directory
    ftp.cwd(pathFTP)
    listing = []

    # read all the file names in the directory
    ftp.retrlines("LIST", listing.append)

    # create all the input name (filename) and output (outfilename, filetif, DiFileEnd) names
    filename = __this.product['data']['fname']['r'].format(dtime=Date)
    outfilename = __this.product['data']['fname']['t'].format(dtime=Date)
    DirFileEnd = os.path.join(output_folder,
                              __this.product['data']['fname']['l'].format(dtime=Date))

    msg = 'Downloading "{f}"'.format(f=filename)
    print('Downloading {f}'.format(f=filename))
    __this.Log.write(datetime.datetime.now(), msg=msg)

    # download the global rainfall file
    try:
        local_filename = os.path.join(output_folder, filename)
        lf = open(local_filename, "wb")
        ftp.retrbinary("RETR " + filename, lf.write, 8192)
        lf.close()

        # unzip the file
        zip_filename = os.path.join(output_folder, filename)
        Extract_Data_gz(zip_filename, outfilename)

        # open tiff file
        dataset = Open_tiff_array(outfilename)

        # clip dataset to the given extent
        data = dataset[yID[0]:yID[1], xID[0]:xID[1]]
        data[data < 0] = -9999

        # save dataset as geotiff file
        geo = [lonlim[0], 0.05, 0, latlim[1], 0, -0.05]
        Save_as_tiff(name=DirFileEnd, data=data, geo=geo, projection="WGS84")

        # delete old tif file
        os.remove(outfilename)

    except:
        print("file not exists")
    return True
