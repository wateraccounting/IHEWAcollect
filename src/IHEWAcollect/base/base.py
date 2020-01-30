# -*- coding: utf-8 -*-
"""
**Base**

`Restrictions`

The data and this python file may not be distributed to others without
permission of the WA+ team.

`Description`

Before use this module, set account information
in the ``IHEWAcollect/accounts.yml`` file.

**Examples:**
::

    from IHEWAcollect.base.base import Base
    base = Base(is_print=True)
"""
import os
import sys
import inspect
# import shutil
# import datetime

import yaml

# try:
#     # setup.py
#     from .base import Base
# except ImportError:
#     # PyCharm
#     from src.IHEWAcollect.base.base import Base
#
# PyCharm
# if __name__ == "__main__":
#
# >>> from .base import Base
# ImportError: cannot import name 'base' from '__main__'
# But works for setup.py
#
# >>> from base import Base
# ModuleNotFoundError
#
# PyCharm->Project Structure->"Sources": WaterAccounting\""
# from src.IHEWAcollect.base.base import Base
# OK
#
# PyCharm->Project Structure->"Sources": IHEWAcollect\"src\IHEWAcollect"
# >>> from base import Base
# OK

try:
    from .base.exception import IHEClassInitError,\
        IHEStringError, IHETypeError, IHEKeyError, IHEFileError
except ImportError:
    from IHEWAcollect.base.exception import IHEClassInitError,\
        IHEStringError, IHETypeError, IHEKeyError, IHEFileError


class Base(object):
    """This Base class

    Args:
      product (str): Product name of data products.
      is_print (bool): Is to print status message.
    """
    status = 'Global status.'

    __status = {
        'messages': {
            0: 'S: WA.Base     {f:>20} : status {c}, {m}',
            1: 'E: WA.Base     {f:>20} : status {c}: {m}',
            2: 'W: WA.Base     {f:>20} : status {c}: {m}',
        },
        'code': 0,
        'message': '',
        'is_print': True
    }

    __conf = {
        'file': 'base.yml',
        'path': os.path.join(
            os.getcwd(),
            os.path.dirname(
                inspect.getfile(
                    inspect.currentframe()))),
        'data': {
            'messages': {},
            'products': {}
        },
        'product': {
            'name': '',
            'data': {}
        }
    }

    def __init__(self, product, is_print):
        """Class instantiation
        """
        # Class self.__status['is_print']
        vname, rtype, vdata = 'is_print', bool, is_print
        if self.check_input(vname, rtype, vdata):
            self.__status['is_print'] = vdata
        else:
            self.__status['code'] = 1

        # Class self.__conf['product']['name']
        self.__conf['product']['name'] = product

        # Class self.__conf['data']
        # Class self.__conf['product']['data']
        if self.__status['code'] == 0:
            self._conf()
            self.__status['message'] = '"{f}" product is: "{v}"'.format(
                f=self.__conf['file'],
                v=self.__conf['product']['name'])
        else:
            raise IHEClassInitError('Base') from None

    def _conf(self,):
        """Get configuration

        This function open collect.cfg configuration file.
        """
        fun_name = inspect.currentframe().f_code.co_name
        f_in = os.path.join(self.__conf['path'],
                            self.__conf['file'])

        # self.__conf['data']
        if os.path.exists(f_in):
            conf = yaml.load(open(f_in, 'r'), Loader=yaml.FullLoader)
            # try:
            #     conf = yaml.load(open(f_in, 'r'), Loader=yaml.FullLoader)
            # except yaml.YAMLError as err:
            #     self.__status['code'] = 1
            #     if hasattr(err, 'problem_mark'):
            #         mark = err.problem_mark
            #         print('Position: (%s:%s)' % (mark.line + 1, mark.column + 1))
            for key in conf:
                try:
                    self.__conf['data'][key] = conf[key]
                except KeyError:
                    self.__status['code'] = 1
                    raise IHEKeyError(key, f_in) from None
                else:
                    self.__status['code'] = 0
        else:
            self.__status['code'] = 1
            raise IHEFileError(f_in)from None

        # self.__conf['product']['data']
        product = self.__conf['product']['name']

        vname, rtype, vdata = 'product', str, product
        if self.check_input(vname, rtype, vdata):
            if vdata in self.__conf['data']['products'].keys():
                self.__conf['product']['data'] = \
                    self.__conf['data']['products'][vdata]
            else:
                self.__status['code'] = 1
                raise IHEKeyError(vdata,
                                  self.__conf['data']['products'].keys()) from None
        else:
            self.__status['code'] = 1

        self.__status['message'] = self._status(
            self.__status['messages'],
            cod=self.__status['code'],
            fun=fun_name,
            prt=self.__status['is_print'],
            ext='')

    def _status(self, stdmsg, cod, fun, prt=False, ext='') -> str:
        """Set Status

        Returns:
          str: Status message.
        """
        # Global
        msg = self.__conf['data']['messages'][cod]['msg']
        lvl = self.__conf['data']['messages'][cod]['level']

        # Local
        if ext != '':
            status = stdmsg[lvl].format(
                f=fun, c=cod, m='{m}\nI: {e}'.format(m=msg, e=ext))
        else:
            status = stdmsg[lvl].format(
                f=fun, c=cod, m='{m}'.format(m=msg))

        if prt:
            print(status)

        # Global self.status
        self.status = status

        # Local self.__status['message']
        return status

    def get_status(self) -> str:
        """Get status

        This is the function to get project status.

        Returns:
          str: Status message.
        """
        return self.status

    def get_conf(self, key) -> dict:
        """Get configuration information

        This is the function to get project's configuration data.

        Args:
          key (str): Key name.

        Returns:
          dict: Configuration data.

        :Example:

            >>> import os
            >>> from IHEWAcollect.base.base import Base
            >>> base = Base(is_print=False)
            >>> file = base.get_conf('file')
            >>> print(file)
            base.yml
        """
        if key in self.__conf:
            self.__status['code'] = 0
        else:
            self.__status['code'] = 1
            raise IHEKeyError(key, self.__conf.keys()) from None

        return self.__conf[key]

    def check_input(self, vname, rtype, vdata) -> bool:
        if isinstance(vdata, rtype):
            if rtype == bool:
                # print('I: {k:} = "{v}"'
                #       .format(k=name,
                #               v=ndata))
                return True

            if rtype == str:
                if vdata != '':
                    # print('I: {k:} = "{v}"'
                    #       .format(k=name,
                    #               v=ndata))
                    return True
                else:
                    raise IHEStringError(vname) from None
        else:
            raise IHETypeError(vname, rtype, vdata) from None

    @classmethod
    def check_conf(cls, key, is_print) -> dict:
        """Check configuration information

        This is the function to get user's configuration data.

        **Don't synchronize the details to github.**

        - File to read: ``collect.yml``.

        Args:
          key (str): Key name.

        Returns:
          dict: Configuration data.

        :Example:

            >>> from IHEWAcollect.base.base import Base
            >>> conf = Base.check_conf('data', is_print=False)
            >>> conf['messages'][0]
            {'msg': 'No error', 'level': 0}
        """
        # this_class = cls(is_print)
        return cls(is_print).get_conf(key)


def main():
    from pprint import pprint

    print('\n__location__\n=====')
    __location__ = os.path.join(
        os.getcwd(),
        os.path.dirname(
            inspect.getfile(
                inspect.currentframe())))
    print(__location__)
    print('0.1', inspect.currentframe())
    print('0.2', inspect.getfile(
        inspect.currentframe()))
    print('1. getcwd:', os.getcwd())
    print('2. dirname: ', os.path.dirname(
        inspect.getfile(inspect.currentframe())))

    print('\n__file__\n=====')
    print(__file__)

    print('\nBase: sys.path\n=====')
    pprint(sys.path)

    # # @classmethod

    # Base __init__
    print('\nBase\n=====')
    product = 'GLEAM'
    base = Base(product, is_print=True)

    # Base attributes
    print(product, base._Base__conf['product'])
    # print(base._Base__conf['data']['products'].keys())
    # pprint(base._Base__conf)

    # # Base methods


if __name__ == "__main__":
    main()
