# -*- coding: utf-8 -*-
import os
# import sys
import inspect

import datetime
import numpy as np
import pandas as pd

try:
    from .base.exception import IHEClassInitError,\
        IHEStringError, IHETypeError, IHEKeyError, IHEFileError
except ImportError:
    from IHEWAcollect.base.exception import IHEClassInitError,\
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
        'path': '',
        'file': {
            'i': '',
            'o': ''
        },
        'time': {
            's': datetime.datetime.now(),
            'e': datetime.datetime.now()
        },
        'dtime': {
            'r': [],
            'i': 0
        },
        'data': {}
    }
    product = {}
    data = np.ndarray

    def __init__(self, workspace, product, is_print, **kwargs):
        """Class instantiation
        """
        # Class self.__status['is_print']
        self.__status['is_print'] = is_print

        # Class self.__conf['path']
        self.__conf['path'] = workspace
        self.product = product
        self._dtime()

    def set_status(self, fun='', prt=False, ext=''):
        """Set status

        Args:
          fun (str): Function name.
          prt (bool): Is to print on screen?
          ext (str): Extra message.
        """
        self.status = self._status(self.__status['messages'],
                                   self.__status['code'],
                                   fun, prt, ext)

    def _dtime(self):
        time = self.__conf['time']
        dtime = self.__conf['dtime']

        if self.__status['code'] == 0:
            time = self.product['data']['time']
            perd = self.product['period']
            freq = self.product['freq']

            if isinstance(time['s'], datetime.date):
                tmp_dtime = time['s']
                time['s'] = \
                    datetime.datetime(tmp_dtime.year, tmp_dtime.month, tmp_dtime.day)
            if isinstance(time['e'], datetime.date):
                tmp_dtime = time['e']
                time['e'] = \
                    datetime.datetime(tmp_dtime.year, tmp_dtime.month, tmp_dtime.day)
            if isinstance(perd['s'], datetime.date):
                tmp_dtime = perd['s']
                perd['s'] = \
                    datetime.datetime(tmp_dtime.year, tmp_dtime.month, tmp_dtime.day)
            if isinstance(perd['e'], datetime.date):
                tmp_dtime = perd['e']
                perd['e'] = \
                    datetime.datetime(tmp_dtime.year, tmp_dtime.month, tmp_dtime.day)

            if perd['s'] < time['s']:
                print('time: {} < {}'.format(perd['s'], time['s']))
                raise IHEClassInitError('Dtime') from None
            if perd['e'] > time['e']:
                print('time: {} > {}'.format(perd['e'], time['e']))
                raise IHEClassInitError('Dtime') from None

            dtime['r'] = pd.date_range(perd['s'], perd['e'], freq=freq)
            dtime['i'] = 0

            self.__conf['time'] = time
            self.__conf['dtime'] = dtime
        return dtime

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
