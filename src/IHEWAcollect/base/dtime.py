# -*- coding: utf-8 -*-
import os
# import sys
import inspect

import datetime
import pandas as pd

try:
    from .base.exception import IHEClassInitError,\
        IHEStringError, IHETypeError, IHEKeyError, IHEFileError
except ImportError:
    from src.IHEWAcollect.base.exception import IHEClassInitError,\
        IHEStringError, IHETypeError, IHEKeyError, IHEFileError


class Dtime(object):
    status = 'Global status.'

    __status = {
        'messages': {
            0: 'S: WA.Dtime    {f:>20} : status {c}, {m}',
            1: 'E: WA.Dtime    {f:>20} : status {c}: {m}',
            2: 'W: WA.Dtime    {f:>20} : status {c}: {m}',
        },
        'code': 0,
        'message': '',
        'is_print': True
    }

    __conf = {
        'file': '',
        'path': '',
        'data': {}
    }

    def __init__(self, workspace, is_print, **kwargs):
        """Class instantiation
        """
        # Class self.__status['is_print']
        self.__status['is_print'] = is_print

        # Class self.__conf['path']
        self.__conf['path'] = workspace

    def check_time_limit(self, dtime_s, dtime_e, conf_time, arg_resolution):
        # Check Startdate and Enddate
        dtime_s, dtime_e = None, None

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


    def get_time_range(self, dtime_s, dtime_e, arg_resolution):
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


def main():
    from pprint import pprint

    # @classmethod

    # Dtime __init__
    print('\nDtime\n=====')
    path = os.path.join(
        os.getcwd(),
        os.path.dirname(
            inspect.getfile(
                inspect.currentframe())),
        '../', '../', '../', 'tests'
    )
    dtime = Dtime(path, is_print=True)

    # Dtime attributes
    print('\ndtime._Dtime__conf:\n=====')
    pprint(dtime._Dtime__conf)
    # print(dtime._Dtime__conf['data'].keys())

    # Dtime methods
    # print('\ndtime.Base.get_status()\n=====')
    # pprint(dtime.get_status())


if __name__ == "__main__":
    main()
