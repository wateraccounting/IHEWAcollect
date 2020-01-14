# -*- coding: utf-8 -*-
"""
**utils**

`Restrictions`

The data and this python file may not be distributed to others without
permission of the WA+ team.

`Description`

Utilities for IHEWAcollect template modules.
"""
import os

import numpy as np
import pandas as pd

import gzip


def unzip_gz(file, outfile):
    """Extract zip file

    This function extract zip file as gz file.

    Args:
      file (str): Name of the file that must be unzipped.
      outfile (str): Directory where the unzipped data must be stored.

    :Example:

        >>> import os
        >>> from IHEWAcollect.base.download import Download
    """

    with gzip.GzipFile(file, 'rb') as zf:
        file_content = zf.read()
        save_file_content = open(outfile, 'wb')
        save_file_content.write(file_content)
    save_file_content.close()
    zf.close()
    os.remove(file)


def ihewa_latlon_lim(lat, lon, conf_lat, conf_lon):
    """

    :param lat:
    :param lon:
    :param conf_lat:
    :param conf_lon:
    :return:
    """
    latlim, lonlim = None, None

    if lat[0] < conf_lat.s or lat[1] > conf_lat.n:
        print(
            'Latitude above 70N or below 60S is not possible. Value set to maximum')
        latlim[0] = np.max(lat[0], conf_lat.s)
        latlim[1] = np.min(lat[1], conf_lat.n)

    if lon[0] < conf_lon.w or lon[1] > conf_lon.e:
        print(
            'Longitude must be between 180E and 180W. Now value is set to maximum')
        lonlim[0] = np.max(lon[0], conf_lon.w)
        lonlim[1] = np.min(lon[1], conf_lon.e)

    return latlim, lonlim


def ihewa_latlon_index(lat, lon, conf_dem):
    latid, lonid = None, None
    # # Define IDs
    # latid = 3000 - np.int16(
    #     np.array(
    #         [np.ceil((latlim[1] + 60) * 20), np.floor((latlim[0] + 60) * 20)]))
    # lonid = np.int16(
    #     np.array(
    #         [np.floor((lonlim[0]) * 20), np.ceil((lonlim[1]) * 20)]) + 3600)

    pass


def ihewa_dtime_lim(dtime_s, dtime_e, conf_time, arg_resolution):
    dtime_s, dtime_e = None, None

    # Check Startdate and Enddate
    if not dtime_s:
        if arg_resolution == 'weekly':
            dtime_s = pd.Timestamp(conf_time.s)
        if arg_resolution == 'daily':
            dtime_s = pd.Timestamp(conf_time.s)
    if not dtime_e:
        if arg_resolution == 'weekly':
            dtime_e = pd.Timestamp(conf_time.e)
        if arg_resolution == 'daily':
            dtime_e = pd.Timestamp(conf_time.e)

    # Make a panda timestamp of the date
    try:
        dtime_e = pd.Timestamp(dtime_e)
    except BaseException:
        dtime_e = dtime_e

    return dtime_s, dtime_e


def ihewa_dtime_range(dtime_s, dtime_e, arg_resolution):
    dtime_r = None

    # if TimeStep == 'daily':
    #     # Define Dates
    #     Dates = pd.date_range(Startdate, Enddate, freq='D')
    #
    # if TimeStep == 'weekly':
    #     # Define the Startdate of ALEXI
    #     DOY = datetime.datetime.strptime(Startdate,
    #                                      '%Y-%m-%d').timetuple().tm_yday
    #     Year = datetime.datetime.strptime(Startdate,
    #                                       '%Y-%m-%d').timetuple().tm_year
    #
    #     # Change the startdate so it includes an ALEXI date
    #     DOYstart = int(math.ceil(DOY / 7.0) * 7 + 1)
    #     DOYstart = str('%s-%s' % (DOYstart, Year))
    #     Day = datetime.datetime.strptime(DOYstart, '%j-%Y')
    #     Month = '%02d' % Day.month
    #     Day = '%02d' % Day.day
    #     Date = (str(Year) + '-' + str(Month) + '-' + str(Day))
    #     DOY = datetime.datetime.strptime(Date,
    #                                      '%Y-%m-%d').timetuple().tm_yday
    #     # The new Startdate
    #     Date = pd.Timestamp(Date)
    #
    #     # amount of Dates weekly
    #     dtime_r = pd.date_range(Date, Enddate, freq='7D')

    return dtime_r

