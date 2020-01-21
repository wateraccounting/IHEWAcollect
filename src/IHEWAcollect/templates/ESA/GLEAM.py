# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
"""
Authors: Tim Hessels
         UNESCO-IHE 2016
Contact: t.hessels@unesco-ihe.org
Repository: https://github.com/wateraccounting/watools
Module: Collect/GLEAM
"""

# import general python modules
import os
import sys
import glob

import datetime
import calendar

from joblib import Parallel, delayed
import paramiko

import numpy as np
import pandas as pd
from netCDF4 import Dataset

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
    This function downloads GLEAM ET data

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

    # Make an array of the days of which the ET is taken
    Dates = pd.date_range(Startdate, Enddate, freq=TimeFreq)

    YearsDownloadstart = str(Startdate[0:4])
    YearsDownloadend = str(Enddate[0:4])
    Years = range(int(YearsDownloadstart), int(YearsDownloadend) + 1)

    # Define directory and create it if not exists
    output_folder = folder['l']

    # String Parameters
    if TimeCase == 'daily':
        VarCode = __this.product['variable']
        FTPprefix = __this.product['data']['dir']

    elif TimeCase == 'monthly':
        VarCode = __this.product['variable']
        FTPprefix = __this.product['data']['dir']

        # Get end of month for Enddate
        monthDownloadend = str(Enddate[5:7])
        End_month = calendar.monthrange(int(YearsDownloadend), int(monthDownloadend))[1]
        Enddate = '%d-%02d-%d' % (int(YearsDownloadend), int(monthDownloadend), int(End_month))
    else:
        raise KeyError("The input time interval is not supported")

    # Collect the data from the GLEAM webpage and returns the data and lat and long in meters of those tiles
    try:
        results = False
        Collect_data(FTPprefix, Years, output_folder, Waitbar)
    except BaseException as err:
        msg = "\nWas not able to download file with date {}".format(Years)
        print('{}\n{}'.format(msg, str(err)))
        __this.Log.write(datetime.datetime.now(),
                         msg='{}\n{}'.format(msg, str(err)))
    else:
        # Pass variables to parallel function and run
        args = [output_folder, latlim, lonlim, VarCode, TimeCase]
        if not cores:
            for Date in Dates:
                RetrieveData(Date, args)
                # if Waitbar == 1:
                #     amount += 1
                #     WaitbarConsole.printWaitBar(amount, total_amount, prefix='Progress:',
                #                                 suffix='Complete', length=50)
            results = True
        else:
            results = Parallel(n_jobs=cores)(delayed(RetrieveData)(Date, args)
                                             for Date in Dates)

    # Create Waitbar
    # print('\nProcess the GLEAM data')
    # if Waitbar == 1:
    #     import watools.Functions.Start.WaitbarConsole as WaitbarConsole
    #     total_amount = len(Dates)
    #     amount = 0
    #     WaitbarConsole.printWaitBar(amount, total_amount, prefix='Progress:',
    #                                 suffix='Complete', length=50)

    # Remove all .hdf files
    # os.chdir(output_folder)
    # files = glob.glob("*.nc")
    # for f in files:
    #     os.remove(os.path.join(output_folder, f))

    return (results)


def RetrieveData(Date, args):
    """
    This function retrieves GLEAM ET data for a given date from the
    www.gleam.eu server.

    Keyword arguments:
    Date -- 'yyyy-mm-dd'
    args -- A list of parameters defined in the DownloadData function.
    """
    # Argument
    [output_folder, latlim, lonlim, VarCode, TimeCase] = args

    # Adjust latlim to GLEAM dataset
    latlim1 = [latlim[1] * -1, latlim[0] * -1]

    # select the spatial dataset
    Ystart = int(np.floor((latlim1[0] + 90) / 0.25))
    Yend = int(np.ceil((latlim1[1] + 90) / 0.25))
    Xstart = int(np.floor((lonlim[0] + 180) / 0.25))
    Xend = int(np.ceil((lonlim[1] + 180) / 0.25))

    Year = Date.year
    Month = Date.month

    filename = __this.product['data']['fname']['r'].format(dtime=Date)
    # if Product == "ET":
    #     filename = 'E_' + str(Year) + '_GLEAM_v3.2b.nc'
    # if Product == "ETpot":
    #     filename = 'Ep_' + str(Year) + '_GLEAM_v3.2b.nc'

    local_filename = os.path.join(output_folder, filename)

    f = Dataset(local_filename, mode='r')

    if TimeCase == 'monthly':

        # defines the start and end of the month
        Datesend1 = str(Date)
        Datesend2 = Datesend1.replace(Datesend1[8:10], "01")
        Datesend3 = Datesend2[0:10]
        Datesend4 = Datesend1[0:10]
        Datestart = pd.date_range(Datesend3, Datesend4, freq='MS')

        # determine the DOY-1 and DOYend (those are use to define the temporal boundaries of the yearly data)
        DOY = int(Datestart[0].strftime('%j'))
        DOYend = int(Date.strftime('%j'))
        DOYDownload = DOY - 1
        Day = 1

        variable = __this.product['data']['variable']
        Data = f.variables[variable][DOYDownload:DOYend, Xstart:Xend, Ystart:Yend]

        data = np.array(Data)
        f.close()

        # Sum ET data in time and change the no data value into -999
        dataSum = sum(data, 1)
        dataSum[dataSum < -100] = -999.000
        dataCor = np.swapaxes(dataSum, 0, 1)

    if TimeCase == 'daily':
        Day = Date.day

        # Define the DOY, DOY-1 is taken from the yearly dataset
        DOY = int(Date.strftime('%j'))
        DOYDownload = DOY - 1

        variable = __this.product['data']['variable']
        Data = f.variables[variable][DOYDownload, Xstart:Xend, Ystart:Yend]
        data = np.array(Data)
        f.close()

        data[data < -100] = -999.000
        dataCor = np.swapaxes(data, 0, 1)

    # The Georeference of the map
    geo_in = [lonlim[0], 0.25, 0.0, latlim[1], 0.0, -0.25]

    # Name of the map
    dataset_name = VarCode + '_' + str(Year) + '.' + str(Month).zfill(2) + '.' + str(Day).zfill(2) + '.tif'
    output_file = os.path.join(output_folder, dataset_name)

    # save data as tiff file
    Save_as_tiff(name=output_file, data=dataCor, geo=geo_in, projection="WGS84")

    return True


def Collect_data(FTPprefix, Years, output_folder, Waitbar):
    '''
    This function downloads all the needed GLEAM files from hydras.ugent.be as a nc file.

    Keywords arguments:
    FTPprefix -- FTP path to the GLEAM data
    Date -- 'yyyy-mm-dd'
    output_folder -- 'C:/file/to/path/'
    '''
    # account of the SFTP server (only password is missing)
    username = __this.account['data']['username']
    password = __this.account['data']['password']
    ftpserver = __this.product['url'].split(':')[0]
    ftpport = __this.product['url'].split(':')[-1]
    # server = 'hydras.ugent.be'
    # portnumber = 2225

    # Create Waitbar
    # if Waitbar == 1:
    #     import watools.Functions.Start.WaitbarConsole as WaitbarConsole
    #     total_amount2 = len(Years)
    #     amount2 = 0
    #     WaitbarConsole.printWaitBar(amount2, total_amount2, prefix='Progress:',
    #                                 suffix='Complete', length=50)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ftpserver, port=ftpport, username=username, password=password)
    ftp = ssh.open_sftp()

    for year in Years:
        # directory = os.path.join(FTPprefix, '%d' % year)
        # filename = 'E_' + str(year) + '_GLEAM_v3.2b.nc'
        directory = __this.product['data']['dir'].format(dtime=pd.Timestamp('{}-01-01'.format(year)))
        filename = __this.product['data']['fname']['r'].format(dtime=pd.Timestamp('{}-01-01'.format(year)))

        local_filename = os.path.join(output_folder, filename)

        fname = os.path.split(local_filename)[-1]
        msg = 'Downloading "{f}"'.format(f=fname)
        print('Downloading {f}'.format(f=fname))
        __this.Log.write(datetime.datetime.now(), msg=msg)

        if not os.path.exists(local_filename):
            ftp.chdir(directory)

            ftp.get(filename, local_filename)

        # if Waitbar == 1:
        #     amount2 += 1
        #     WaitbarConsole.printWaitBar(amount2, total_amount2, prefix='Progress:',
        #                                 suffix='Complete', length=50)

    ftp.close()
    ssh.close()

    return ()