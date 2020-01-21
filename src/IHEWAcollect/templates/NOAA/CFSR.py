# -*- coding: utf-8 -*-
"""
Authors: Tim Hessels
         UNESCO-IHE 2016
Contact: t.hessels@unesco-ihe.org
Repository: https://github.com/wateraccounting/watools
Module: Collect/CFSR
"""
# General modules
import os
import sys

import datetime

import re
from joblib import Parallel, delayed
import pycurl

import pandas as pd
import numpy as np

from netCDF4 import Dataset

# WA+ modules
# from watools.Collect.CFSR.Download_data_CFSR import Download_data
# IHEWAcollect Modules
try:
    from ..collect import \
        Extract_Data_gz, Open_tiff_array, Save_as_tiff, \
        Convert_grb2_to_nc
    # from ..gis import GIS
    # from ..dtime import Dtime
    from ..util import Log
except ImportError:
    from IHEWAcollect.templates.collect import \
        Extract_Data_gz, Open_tiff_array, Save_as_tiff, \
        Convert_grb2_to_nc
    # from IHEWAcollect.templates.gis import GIS
    # from IHEWAcollect.templates.dtime import Dtime
    from IHEWAcollect.templates.util import Log


__this = sys.modules[__name__]


def DownloadData(status, conf):
    """
    This function collects daily CFSR data in geotiff format

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

    Version = int(conf['product']['version'][-1])
    TimeStep = conf['product']['resolution']
    Var = conf['product']['variable']
    freq = conf['product']['freq']
    latlim = conf['product']['data']['lat']
    lonlim = conf['product']['data']['lon']

    folder = conf['folder']

    # Creates an array of the days of which the ET is taken
    Dates = pd.date_range(Startdate, Enddate, freq=freq)

    # # Create Waitbar
    # if Waitbar == 1:
    #     import watools.Functions.Start.WaitbarConsole as WaitbarConsole
    #     total_amount = len(Dates)
    #     amount = 0
    #     WaitbarConsole.printWaitBar(amount, total_amount, prefix='Progress:', suffix='Complete', length=50)

    # Check the latitude and longitude and otherwise set lat or lon on greatest extent
    # if bbox['s'] < latlim['s'] or bbox['n'] > latlim['n']:
    #     bbox['s'] = np.max(bbox['s'], latlim['s'])
    #     bbox['n'] = np.min(bbox['n'], latlim['n'])
    # if bbox['w'] < lonlim['w'] or bbox['e'] > lonlim['e']:
    #     bbox['w'] = np.max(bbox['w'], lonlim['w'])
    #     bbox['e'] = np.min(bbox['e'], lonlim['e'])

    latlim = [bbox['s'], bbox['n']]
    lonlim = [bbox['w'], bbox['e']]

    # Make directory for the CFSR data
    output_folder = folder['l']

    # Pass variables to parallel function and run
    args = [output_folder, latlim, lonlim, Var, Version]
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

    # # Remove all .nc and .grb2 files
    # for f in os.listdir(output_folder):
    #     if re.search(".nc", f):
    #         os.remove(os.path.join(output_folder, f))
    # for f in os.listdir(output_folder):
    #     if re.search(".grb2", f):
    #         os.remove(os.path.join(output_folder, f))
    # for f in os.listdir(output_folder):
    #     if re.search(".grib2", f):
    #         os.remove(os.path.join(output_folder, f))

    return results


def RetrieveData(Date, args):
    # unpack the arguments
    [output_folder, latlim, lonlim, Var, Version] = args

    # Name of the outputfile
    Outputname = __this.product['data']['fname']['l'].format(dtime=Date)

    msg = 'Downloading "{f}"'.format(f=Outputname)
    print('Downloading {f}'.format(f=Outputname))
    __this.Log.write(datetime.datetime.now(), msg=msg)

    # Create the total end output name
    outputnamePath = os.path.join(output_folder, Outputname)

    # If the output name not exists than create this output
    if not os.path.exists(outputnamePath):

        local_filename = Download_data(Date, Version, output_folder, Var)

        # convert grb2 to netcdf (wgrib2 module is needed)
        for i in range(0, 4):
            nameNC = __this.product['data']['fname']['t'].format(dtime=Date, ipart=str(i+1))

            # Total path of the output
            FileNC6hour = os.path.join(output_folder, nameNC)

            # Band number of the grib data which is converted in .nc
            band = (int(Date.strftime('%d')) - 1) * 28 + (i + 1) * 7

            # Convert the data
            Convert_grb2_to_nc(local_filename, FileNC6hour, band)

        if Version == 1:
            if Date < pd.Timestamp(pd.datetime(2011, 1, 1)):
                # Convert the latlim and lonlim into array
                Xstart = np.floor((lonlim[0] + 180.1562497) / 0.3125)
                Xend = np.ceil((lonlim[1] + 180.1562497) / 0.3125) + 1
                Ystart = np.floor((latlim[0] + 89.9171038899) / 0.3122121663)
                Yend = np.ceil((latlim[1] + 89.9171038899) / 0.3122121663)

                # Create a new dataset
                Datatot = np.zeros([576, 1152])

            else:
                Version = 2

        if Version == 2:
            # Convert the latlim and lonlim into array
            Xstart = np.floor((lonlim[0] + 180.102272725) / 0.204545)
            Xend = np.ceil((lonlim[1] + 180.102272725) / 0.204545) + 1
            Ystart = np.floor((latlim[0] + 89.9462116040955806) / 0.204423)
            Yend = np.ceil((latlim[1] + 89.9462116040955806) / 0.204423)

            # Create a new dataset
            Datatot = np.zeros([880, 1760])

        # Open 4 times 6 hourly dataset
        for i in range(0, 4):
            nameNC = __this.product['data']['fname']['t'].format(dtime=Date, ipart=str(i+1))
            FileNC6hour = os.path.join(output_folder, nameNC)

            f = Dataset(FileNC6hour, mode='r')
            Data = f.variables['Band1'][0:int(Datatot.shape[0]), 0:int(Datatot.shape[1])]
            f.close()
            data = np.array(Data)
            Datatot = Datatot + data

        # Calculate the average in W/m^2 over the day
        DatatotDay = Datatot / 4
        DatatotDayEnd = np.zeros([int(Datatot.shape[0]), int(Datatot.shape[1])])
        DatatotDayEnd[:,0:int(Datatot.shape[0])] = DatatotDay[:, int(Datatot.shape[0]):int(Datatot.shape[1])]
        DatatotDayEnd[:,int(Datatot.shape[0]):int(Datatot.shape[1])] = DatatotDay[:, 0:int(Datatot.shape[0])]

        # clip the data to the extent difined by the user
        DatasetEnd = DatatotDayEnd[int(Ystart):int(Yend), int(Xstart):int(Xend)]

        # save file
        if Version == 1:
            pixel_size = 0.3125
        if Version == 2:
            pixel_size = 0.204545
        geo = [lonlim[0], pixel_size, 0, latlim[1], 0, -pixel_size]
        Save_as_tiff(data=np.flipud(DatasetEnd), name=outputnamePath, geo=geo, projection="WGS84")

        os.remove(local_filename)
        for i in range(0, 4):
            nameNC = __this.product['data']['fname']['t'].format(dtime=Date, ipart=str(i+1))
            FileNC6hour = os.path.join(output_folder, nameNC)
            os.remove(FileNC6hour)

    return()


def Download_data(Date, Version, output_folder, Var):
    """
    This function downloads CFSR data from the FTP server
    For - CFSR:    https://nomads.ncdc.noaa.gov/data/cfsr/
    - CFSRv2:  http://nomads.ncdc.noaa.gov/modeldata/cfsv2_analysis_timeseries/

    Keyword arguments:
    Date -- pandas timestamp day
    Version -- 1 or 2 (1 = CFSR, 2 = CFSRv2)
    output_folder -- The directory for storing the downloaded files
    Var -- The variable that must be downloaded from the server ('dlwsfc','uswsfc','dswsfc','ulwsfc')
    """
    # Define the filename that must be downloaded
    if Version == 1:
        filename = Var + '.gdas.' + str(Date.strftime('%Y')) + str(Date.strftime('%m')) + '.grb2'
    if Version == 2:
        filename = Var + '.gdas.' + str(Date.strftime('%Y')) + str(Date.strftime('%m')) + '.grib2'

    try:
         # download the file when it not exist
        local_filename = os.path.join(output_folder, filename)
        if not os.path.exists(local_filename):
            Downloaded = 0
            Times = 0
            while Downloaded == 0:
                # Create the command and run the command in cmd
                FTP_name = '{}{}{}'.format(__this.product['url'].format(dtime=Date),
                                           __this.product['data']['dir'].format(dtime=Date),
                                           filename)
                # if Version == 1:
                #     FTP_name = 'https://nomads.ncdc.noaa.gov/data/cfsr/' + Date.strftime('%Y') + Date.strftime('%m')+ '/' + filename
                #
                # if Version == 2:
                #     FTP_name = 'https://nomads.ncdc.noaa.gov/modeldata/cfsv2_analysis_timeseries/' + Date.strftime('%Y') + '/' + Date.strftime('%Y') + Date.strftime('%m')+ '/' + filename

                curl = pycurl.Curl()
                curl.setopt(pycurl.URL, FTP_name)
                fp = open(local_filename, "wb")
                curl.setopt(pycurl.SSL_VERIFYPEER, 0)
                curl.setopt(pycurl.SSL_VERIFYHOST, 0)
                curl.setopt(pycurl.WRITEDATA, fp)
                curl.perform()
                curl.close()
                fp.close()
                statinfo = os.stat(local_filename)
                if int(statinfo.st_size) > 10000:
                    Downloaded = 1
                else:
                    Times += 1
                    if Times == 10:
                        Downloaded = 1
    except:
        print('Was not able to download the CFSR file from the FTP server')

    return(local_filename)