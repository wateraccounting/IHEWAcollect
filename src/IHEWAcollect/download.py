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
import datetime

try:
    from .base.exception import IHEClassInitError,\
        IHEStringError, IHETypeError, IHEKeyError, IHEFileError
except ImportError:
    from src.IHEWAcollect.base.exception import IHEClassInitError,\
        IHEStringError, IHETypeError, IHEKeyError, IHEFileError

try:
    from .base.user import User
    from .base.gis import GIS
    from .base.dtime import Dtime
    from .base.util import Extract
except ImportError:
    from src.IHEWAcollect.base.user import User
    from src.IHEWAcollect.base.gis import GIS
    from src.IHEWAcollect.base.dtime import Dtime
    from src.IHEWAcollect.base.util import Extract


class Download(User, GIS, Dtime,
               Extract):
    """This Download class

    Description

    - product = 'ALEXI'
    - version = 'v1'
    - parameter = 'Evaporation'
    - resolution = 'daily'
    - variable = 'ETa'

    Download

    - prepare()
    - start()
    - finish()

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
        'time': {
            'start': None,
            'now': None,
            'end': None
        },
        'log': {
            'fname': 'log-{t}.txt',
            'file': '{path}/log-{t}.txt',
            'fp': None,
            'status': -1,  # -1: not found, 0: closed, 1: opened
        },

        'path': '',
        'account': {
            'name': '',
            'data': {}
        },
        'product': {
            'name': '',
            'version': '',
            'parameter': '',
            'resolution': '',
            'variable': '',
            'data': {}
        },
        'template': {
            'name': '',
            'data': {}
        }
    }

    def __init__(self, workspace='',
                 product='', version='', parameter='', resolution='', variable='',
                 is_status=True, **kwargs):
        """Class instantiation
        """
        tmp_product_conf = {
            'version': version,
            'parameter': parameter,
            'resolution': resolution,
            'variable': variable
        }

        # Class self.__status['is_print']
        vname, rtype, vdata = 'is_status', bool, is_status
        if self.check_input(vname, rtype, vdata):
            self.__status['is_print'] = vdata
        else:
            self.__status['code'] = 1

        # Class self.__conf['path']
        vname, rtype, vdata = 'workspace', str, workspace
        if self.check_input(vname, rtype, vdata):
            self.__conf['path'] = vdata
        else:
            self.__status['code'] = 1

        rtype = str
        for vname, vdata in tmp_product_conf.items():
            if self.check_input(vname, rtype, vdata):
                self.__conf['product'][vname] = vdata
            else:
                self.__status['code'] = 1

        # super(Download, self).__init__(workspace, account, is_status, **kwargs)
        if self.__status['code'] == 0:
            User.__init__(self, workspace, product, is_status, **kwargs)
            GIS.__init__(self, workspace, is_status, **kwargs)
            Dtime.__init__(self, workspace, is_status, **kwargs)
        else:
            raise IHEClassInitError('Download') from None


        # Class GIS
        # self.latlim = self.var['lat']
        # self.lonlim = self.var['lon']
        # self.timlim = self.var['time']

        # Class Dtime

        # Class Download
        if self.__status['code'] == 0:
            # TODO, 20200115, QPan, delete
            self.prepare()
            self.start()
            self.finish()

            self.__status['message'] = ''
        else:
            raise IHEClassInitError('Download') from None

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

    def prepare(self):
        self.get_time()
        self.get_log()
        self.get_account()
        self.get_product()
        self.get_template()
        # get_folder

    def start(self):
        # get_url
        # get_auth
        self.write_log(msg='msg')

    def finish(self):
        self.close_log()
        # clean_folder

    def get_time(self):
        # Class self.__conf['time']
        time = self.__conf['time']

        if self.__status['code'] == 0:
            now = datetime.datetime.now()

            self.__conf['time']['start'] = now
            self.__conf['time']['now'] = now
            self.__conf['time']['end'] = now
        return time

    def get_log(self):
        # Class self.__conf['log']
        status = -1
        log = self.__conf['log']

        if self.__status['code'] == 0:
            time_s = self.__conf['time']['start']
            time_s_str = time_s.strftime('%Y-%m-%d %H:%M:%S.%f')

            fname = 'log-{t}.txt'.format(t=time_s.strftime('%Y%m%d%H%M%S%f'))

            path = self.__conf['path']
            file = os.path.join(path, fname)

            # TODO, 20200115, QPan, code
            # -1: not found, 0: closed, 1: opened
            if os.path.isfile(file):
                status = 0
            else:
                print('Create log file: {f}'.format(f=fname))
                txt = 'IHEWAcollect created on {t}'.format(t=time_s_str)

                fp = open(file, 'w+')
                fp.write('{}\n'.format(txt))
                status = 0

            self.__conf['log']['fname'] = fname
            self.__conf['log']['file'] = file
            self.__conf['log']['fp'] = fp
            self.__conf['log']['status'] = status
        return log

    def write_log(self, msg=''):
        time_n = datetime.datetime.now()
        time_n_str = time_n.strftime('%Y-%m-%d %H:%M:%S.%f')
        self.__conf['time']['now'] = time_n

        fp = self.__conf['log']['fp']

        txt = '{t}: {msg}'.format(t=time_n_str, msg=msg)
        fp.write('{}\n'.format(txt))

    def close_log(self):
        time_e = datetime.datetime.now()
        time_e_str = time_e.strftime('%Y-%m-%d %H:%M:%S.%f')
        self.__conf['time']['end'] = time_e

        fp = self.__conf['log']['fp']

        txt = 'IHEWAcollect finished on {t}'.format(t=time_e_str)
        fp.write('{}\n'.format(txt))
        fp.close()
        self.__conf['log']['fp'] = None

    def get_account(self):
        # Class self.__conf['account'] <- User.account
        account = self.__conf['account']

        if self.__status['code'] == 0:
            account['name'] = self._User__conf['account']['name']
            account['data'] = self._User__conf['account']['data']

            self.__conf['account']['name'] = account['name']
            self.__conf['account']['data'] = account['data']
        return account

    def get_product(self):
        # Class self.__conf['product'] <- Base.product
        product = self.__conf['product']
        version = product['version']
        parameter = product['parameter']
        resolution = product['resolution']
        variable = product['variable']

        if self.__status['code'] == 0:
            product['name'] = self._Base__conf['product']['name']
            product['data'] = self._Base__conf['product']['data']

            keys = product['data'].keys()
            if version not in keys:
                self.__status['code'] = 1
                raise IHEKeyError(version, keys) from None

            keys = product['data'][
                version].keys()
            if parameter not in keys:
                self.__status['code'] = 1
                raise IHEKeyError(parameter, keys) from None

            keys = product['data'][
                version][parameter].keys()
            if resolution not in keys:
                self.__status['code'] = 1
                raise IHEKeyError(resolution, keys) from None

            keys = product['data'][
                version][parameter][resolution]['variables'].keys()
            if variable not in keys:
                self.__status['code'] = 1
                raise IHEKeyError(variable, keys) from None

            self.__conf['product']['name'] = product['name']
            self.__conf['product']['data'] = product['data'][
                version][parameter][resolution]['variables'][variable]
        return product

    def get_template(self):
        # Class self.__conf['template'] <- Base.product
        template = self.__conf['template']

        if self.__status['code'] == 0:
            template['name'] = self._Base__conf['product']['name']
            # template['data'] = self._Base__conf['product']['data']

            self.__conf['template']['name'] = template['name']
        return template

    def load_lib(self, protocol, method):
        lib = None

        # Define library, "protocol" and "method"
        if method == 'get':
            lib = '.'.join(protocol, method)
        elif method == 'post':
            lib = '.'.join(protocol, method)
        else:
            raise ValueError('Unknown method: {v}'.format(v=method))

        # Load library
        self.__conf['template']['lib'] = lib
        return lib

    def get_folder(self, path):
        folder = {
            'r': '',
            't': '',
            'l': ''
        }
        # Define folder

        # # Define directory and create it if not exists
        # output_folder = os.path.join(Dir, 'Evaporation', 'ALEXI', 'Weekly')
        # if not os.path.exists(output_folder):
        #     os.makedirs(output_folder)

        # Create folder

        # Clean folder

        self.__conf['template']['folder'] = folder
        return folder

    def create_folder(self, name):
        # # Define directory and create it if not exists
        # output_folder = os.path.join(Dir, 'Evaporation', 'ALEXI', 'Weekly')
        # if not os.path.exists(output_folder):
        #     os.makedirs(output_folder)

        # output_folder = os.path.join(Dir, 'Evaporation', 'ALEXI', 'Daily')
        # if not os.path.exists(output_folder):
        #     os.makedirs(output_folder)
        pass

    def get_url(self):
        pass

    def get_auth(self):
        pass

    def get_rfile(self):
        pass

    def get_tfile(self):
        pass

    def get_lfile(self):
        pass

    def clean_folder(self, name):
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
        '../', '../', 'tests'
    )
    product = 'ALEXI'
    download = Download(workspace=path,
                        product=product,
                        version='v1',
                        parameter='evapotranspiration',
                        resolution='daily',
                        variable='ETA',
                        is_status=False)

    # # Base attributes
    # print('\ndownload._Base__conf\n=====')
    # pprint(download._Base__conf)

    # User attributes
    print('\ndownload._User__conf\n=====')
    pprint(download._User__conf['account'])

    # # GIS attributes
    # print('\ndownload._GIS__conf:\n=====')
    # pprint(download._GIS__conf)

    # # Dtime attributes
    # print('\ndownload._Dtime__conf:\n=====')
    # pprint(download._Dtime__conf)

    # Download attributes
    print('\ndownload._Download__conf()\n=====')
    # pprint(download._Download__conf.keys())
    pprint(download._Download__conf)

    # Download methods
    print('\ndownload.get_status()\n=====')
    pprint(download.get_status())


if __name__ == "__main__":
    main()
