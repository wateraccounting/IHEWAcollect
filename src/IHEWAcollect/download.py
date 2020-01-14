# -*- coding: utf-8 -*-
"""
**Download**

`Restrictions`

The data and this python file may not be distributed to others without
permission of the WA+ team.

`Description`

Before use this module, set account information
in the ``IHEWAcollect/accounts.yml`` file.

**Examples:**
::

    import os
    from IHEWAcollect.base.download import Download
    download = Download(workspace=os.getcwd(),
                        product='ALEXI',
                        version='v1',
                        parameter='evapotranspiration',
                        resolution='daily',
                        variable='ETA',
                        is_status=False)

"""
import os
# import sys
import inspect
# import shutil
# import yaml
# from datetime import datetime

# import numpy as np
# import pandas as pd

try:
    from .base.exception import \
        IHEStringError, IHETypeError, IHEKeyError, IHEFileError
except ImportError:
    from src.IHEWAcollect.base.exception \
        import IHEStringError, IHETypeError, IHEKeyError, IHEFileError

try:
    from .base.accounts import Accounts
except ImportError:
    from src.IHEWAcollect.base.accounts import Accounts

try:
    from .base.gis import GIS
except ImportError:
    from src.IHEWAcollect.base.gis import GIS


class Download(Accounts, GIS):
    """This Download class

    Description

    - product = 'ALEXI',
    - version = 'v1',
    - parameter = 'Evaporation',
    - resolution = 'daily',
    - variable = 'ETa',

    Args:
      workspace (str): Directory to accounts.yml.
      product (str): Product name.
      version (str): Version name.
      parameter (str): Parameter name.
      resolution (str): Resolution name.
      variable (str): Variable name.
      is_status (bool): Is to print status message.
      kwargs (dict): Other arguments.
    """
    status = 'Global status.'

    __status = {
        'messages': {
            0: 'S: WA.Download {f:>20} : status {c}, {m}',
            1: 'E: WA.Download {f:>20} : status {c}: {m}',
            2: 'W: WA.Download {f:>20} : status {c}: {m}',
        },
        'code': 0,
        'message': '',
        'is_print': True
    }

    __conf = {
        'path': '',
        'file': '',
        'product': '',
        'version': '',
        'parameter': '',
        'resolution': '',
        'variable': '',
        'template': '',
        'data': {}
    }

    def __init__(self, workspace='',
                 product='', version='', parameter='', resolution='', variable='',
                 is_status=True, **kwargs):
        """Class instantiation
        """
        wa_args = {
            'product': product,
            'version': version,
            'parameter': parameter,
            'resolution': resolution,
            'variable': variable
        }

        vname, rtype, vdata = 'is_status', bool, is_status
        if self.check_input(vname, rtype, vdata):
            self.__status['is_print'] = vname
        else:
            self.__status['code'] = 1

        vname, rtype, vdata = 'workspace', str, workspace
        if self.check_input(vname, rtype, vdata):
            self.__conf['path'] = vname
        else:
            self.__status['code'] = 1

        rtype = str
        for vname, vdata in wa_args.items():
            if self.check_input(vname, rtype, vdata):
                self.__conf[vname] = vname
            else:
                self.__status['code'] = 1

        Accounts.__init__(self, workspace, product, is_status, **kwargs)
        GIS.__init__(self, workspace, is_status, **kwargs)
        # super(Download, self).__init__(workspace, account, is_status, **kwargs)

        keys = self._Base__conf['data'][
            'products'].keys()
        if product not in keys:
            self.__status['code'] = 1
            raise IHEKeyError(product, keys) from None
        keys = self._Base__conf['data'][
            'products'][product].keys()
        if version not in keys:
            self.__status['code'] = 1
            raise IHEKeyError(version, keys) from None
        keys = self._Base__conf['data'][
            'products'][product][version].keys()
        if parameter not in keys:
            self.__status['code'] = 1
            raise IHEKeyError(parameter, keys) from None
        keys = self._Base__conf['data'][
            'products'][product][version][parameter].keys()
        if resolution not in keys:
            self.__status['code'] = 1
            raise IHEKeyError(resolution, keys) from None
        keys = self._Base__conf['data'][
            'products'][product][version][parameter][resolution]['variables'].keys()
        if variable not in keys:
            self.__status['code'] = 1
            raise IHEKeyError(variable, keys) from None
        self.var = self._Base__conf['data']['products'][
            product][version][parameter][resolution]['variables'][variable]
        self.latlim = self.var['lat']
        self.lonlim = self.var['lon']
        self.timlim = self.var['time']

        if self.__status['code'] == 0:
            # self._conf()
            self.__status['message'] = ''

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

    def check_template(self, account=''):
        if account == 'IHEWA':
            self.__status['template'] = {'IHEWA': 'dat'}
            pass
        elif account == 'ASCAT':
            pass
        elif account == 'CFSR':
            pass
        else:
            raise ValueError('Unknown account: {v}'.format(v=account))
        pass

    def check_method(self, Protocol='', method=''):
        py_lib = 'requests'
        py_method = 'requests.get'

        if Protocol == '':
            pass
        elif Protocol == 'FTP':
            py_lib = 'ftp'

            if method == 'get':
                py_method = '.'.join(py_lib, method)
            elif method == 'post':
                py_method = '.'.join(py_lib, method)
            else:
                raise ValueError('Unknown method: {v}'.format(v=method))
        elif Protocol == 'HTTP':
            py_lib = 'requests'
            # py_lib = 'urllib'
            # py_lib = 'pycurl'

            if method == 'get':
                py_method = '.'.join(py_lib, method)
            elif method == 'post':
                py_method = '.'.join(py_lib, method)
            else:
                raise ValueError('Unknown method: {v}'.format(v=method))
        elif Protocol == 'HTTPS':
            py_lib = 'requests'
            # py_lib = 'urllib'
            # py_lib = 'pycurl'

            if method == 'get':
                py_method = '.'.join(py_lib, method)
            elif method == 'post':
                py_method = '.'.join(py_lib, method)
            else:
                raise ValueError('Unknown method: {v}'.format(v=method))
        elif Protocol == 'TDS':
            py_lib = 'pytds'

            if method == 'get':
                py_method = '.'.join(py_lib, method)
            elif method == 'post':
                py_method = '.'.join(py_lib, method)
            else:
                raise ValueError('Unknown method: {v}'.format(v=method))
        elif Protocol == 'ECMWF':
            py_lib = 'ecmwfapi'

            if method == 'retrieve':
                py_method = '.'.join(py_lib, method)
            else:
                raise ValueError('Unknown method: {v}'.format(v=method))
        else:
            raise ValueError('Unknown method: {v}'.format(v=Protocol))

        return py_method

    def check_version(self, version=''):
        if version == '':
            pass
        elif version == 'v1':
            pass
        elif version == 'v2':
            pass
        elif version == 'v3':
            pass
        else:
            raise ValueError('Unknown version: {v}'.format(v=version))
        pass

    def create_folder(self):
        # # Define directory and create it if not exists
        # output_folder = os.path.join(Dir, 'Evaporation', 'ALEXI', 'Weekly')
        # if not os.path.exists(output_folder):
        #     os.makedirs(output_folder)

        # output_folder = os.path.join(Dir, 'Evaporation', 'ALEXI', 'Daily')
        # if not os.path.exists(output_folder):
        #     os.makedirs(output_folder)
        pass

    def clean_folder(self):
        # os.chdir(output_folder)
        # re = glob.glob("*.dat")
        # for f in re:
        #     os.remove(os.path.join(output_folder, f))
        pass


def main():
    from pprint import pprint

    # @classmethod

    # Download __init__
    print('\nDownload\n=====')
    path = os.path.join(
        os.getcwd(),
        os.path.dirname(
            inspect.getfile(
                inspect.currentframe())),
        '../', '../',
    )
    download = Download(workspace=path,
                        product='ALEXI',
                        version='v1',
                        parameter='evapotranspiration',
                        resolution='daily',
                        variable='ETA',
                        is_status=False)
    # 'Copernicus', is_status=False)

    # # Base attributes
    # print('\ndownload._Base__conf\n=====')
    # pprint(download._Base__conf)
    #
    # print('\n\n=====')
    # for key, val in download._Base__conf['data']['products'].items():
    #     print(key)
    #     print('-----')
    #     pprint(val['meta'])
    #     pprint(val[val['meta']['versions'][0]])
    #
    # # Accounts attributes
    # print('\ndownload._Accounts__conf\n=====')
    # pprint(download._Accounts__conf)
    #
    # # GIS attributes
    # print('\ndownload._GIS__conf:\n=====')
    # pprint(download._GIS__conf)

    # Download attributes
    print('\ndownload._Download__conf()\n=====')
    # pprint(download._Download__conf.keys())
    pprint(download._Download__conf)

    # Download methods
    print('\ndownload.get_status()\n=====')
    pprint(download.get_status())


if __name__ == "__main__":
    main()
