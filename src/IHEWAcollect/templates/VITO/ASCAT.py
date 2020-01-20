# -*- coding: utf-8 -*-
# General modules
import os
import sys
import shutil

import datetime

import requests
from requests.auth import HTTPBasicAuth

import numpy as np
import pandas as pd

import h5py
from netCDF4 import Dataset

# IHEWAcollect Modules
try:
    from ..collect import \
        Extract_Data_gz, Open_tiff_array, Save_as_tiff
    # from ..gis import GIS
    # from ..dtime import Dtime
    from ..util import Log
except ImportError:
    from IHEWAcollect.templates.collect import \
        Extract_Data_gz, Open_tiff_array, Save_as_tiff
    # from IHEWAcollect.templates.gis import GIS
    # from IHEWAcollect.templates.dtime import Dtime
    from IHEWAcollect.templates.util import Log


__this = sys.modules[__name__]


def DownloadData(status, conf):
    """
    This scripts downloads ASCAT SWI data from the VITO server.
    The output files display the Surface Water Index.

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
        Enddate = pd.Timestamp.now()

    # Creates dates library
    Dates = pd.date_range(Startdate, Enddate, freq=freq)

    # Define directory and create it if not exists
    output_folder = folder['l']

    # Create Waitbar
    # if Waitbar == 1:
    #     import watools.Functions.Start.WaitbarConsole as WaitbarConsole
    #     total_amount = len(Dates)
    #     amount = 0
    #     WaitbarConsole.printWaitBar(amount, total_amount, prefix='Progress:',
    #                                 suffix='Complete', length=50)

    # Define IDs
    xID = 1800 + np.int16(np.array([np.ceil((lonlim[0]) * 10),
                                    np.floor((lonlim[1]) * 10)]))

    yID = np.int16(np.array([np.floor((-latlim[1]) * 10),
                             np.ceil((-latlim[0]) * 10)])) + 900

    for Date in Dates:

        # Date as printed in filename
        Filename_out= os.path.join(output_folder,
                                   __this.product['data']['fname']['l'].format(dtime=Date))

        # Define end filename
        Filename_in = __this.product['data']['fname']['r'].format(dtime=Date)

         # Temporary filename for the downloaded global file
        local_filename = os.path.join(output_folder, Filename_in)

        # Download the data from server if the file not exists
        if not os.path.exists(Filename_out):
            try:
                Download_ASCAT_from_VITO(local_filename, Filename_in, Date)
            except BaseException as err:
                msg = "\nWas not able to download file with date %s" % Date
                print('{}\n{}'.format(msg, str(err)))
                __this.Log.write(datetime.datetime.now(),
                                 msg='{}\n{}'.format(msg, str(err)))
            else:
                # Open nc file
                fh = Dataset(local_filename)

                # clip dataset to the given extent
                dataset = fh.variables['SWI_010'][:, yID[0]:yID[1], xID[0]:xID[1]]
                data = np.squeeze(dataset.data, axis=0)
                data = data * 0.5
                data[data > 100.] = -9999
                fh.close()

                # save dataset as geotiff file
                geo = [lonlim[0], 0.1, 0, latlim[1], 0, -0.1]
                Save_as_tiff(name=Filename_out, data=data,
                             geo=geo, projection="WGS84")

                # delete old tif file
                os.remove(os.path.join(local_filename))

        # Adjust waitbar
        # if Waitbar == 1:
        #     amount += 1
        #     WaitbarConsole.printWaitBar(amount, total_amount,
        #                                 prefix='Progress:', suffix='Complete',
        #                                 length=50)


def Download_ASCAT_from_VITO(local_filename, Filename_in, Date):
    """
    This function retrieves ALEXI data for a given date from the
    ftp.wateraccounting.unesco-ihe.org server.

    Restrictions:
    The data and this python file may not be distributed to others without
    permission of the WA+ team due data restriction of the ALEXI developers.

    Keyword arguments:

    """

    # Collect account and FTP information
    username = __this.account['data']['username']
    password = __this.account['data']['password']

    # URL = "https://land.copernicus.vgt.vito.be/PDF/datapool/Vegetation/Soil_Water/SWI_V3/%s/%s/%s/%s/%s" % (year_data, month_data, day_data,
    #                                       ASCAT_name, ASCAT_filename)
    URL = '{}{}{}'.format(__this.product['url'],
                          __this.product['data']['dir'].format(dtime=Date),
                          Filename_in)

    fname = os.path.split(local_filename)[-1]
    msg = 'Downloading "{f}"'.format(f=fname)
    print('Downloading {f}'.format(f=fname))
    __this.Log.write(datetime.datetime.now(), msg=msg)

    # Download the ASCAT data
    try:
        y = requests.get(URL, auth=HTTPBasicAuth(username, password))
    except:
        from requests.packages.urllib3.exceptions import InsecureRequestWarning
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

        y = requests.get(URL, auth=(username, password), verify=False)

    # Write the file in system
    z = open(local_filename, 'wb')
    z.write(y.content)
    z.close()

    return
