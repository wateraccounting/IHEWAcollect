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
import importlib

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
except ImportError:
    from src.IHEWAcollect.base.user import User


class Download(User):
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
      bbox (dict): Spatial range, {'w':, 's':, 'e':, 'n':}.
      period (dict): Time range, {'s':, 'e':}.
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
        'time': {
            'start': None,
            'now': None,
            'end': None
        },
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
            'bbox': [],
            'period': [],
            'data': {}
        },
        'folder': {
            'r': '',
            't': '',
            'l': ''
        },
        'log': {
            'name': 'log.txt',
            'file': '{path}/log-.txt',
            'fp': None,
            'status': -1,  # -1: not found, 0: closed, 1: opened
        },
        'downloader': {
            'name': '',
            'url': '',
            'protocol': '',
            'method': '',
            'freq': '',
            'module': None,
            'data': {}
        }
    }
    __tmp = {
        'name': '',
        'module': None,
        'data': {}
    }

    def __init__(self, workspace='',
                 product='', version='', parameter='', resolution='', variable='',
                 bbox={}, period={},
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
            path = os.path.join(vdata, 'IHEWAcollect')
            if not os.path.exists(path):
                os.makedirs(path)
            self.__conf['path'] = path
        else:
            self.__status['code'] = 1

        rtype = str
        for vname, vdata in tmp_product_conf.items():
            if self.check_input(vname, rtype, vdata):
                self.__conf['product'][vname] = vdata
            else:
                self.__status['code'] = 1
        self.__conf['product']['bbox'] = bbox
        self.__conf['product']['period'] = period

        # super(Download, self).__init__(**kwargs)
        if self.__status['code'] == 0:
            User.__init__(self, workspace, product, is_status, **kwargs)
        else:
            raise IHEClassInitError('Download') from None

        # Class Download
        if self.__status['code'] == 0:
            self._time()
            self._account()
            self._product()
            self._folder()

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

    def prepare(self) -> int:
        """

        Returns:
          int: Status.
        """
        status = -1
        self._log()
        self._downloader()
        self._template()
        return status

    def start(self) -> int:
        """

        Returns:
          int: Status.
        """
        status = -1
        self.__tmp['module'].download()
        self.__tmp['module'].convert()
        self.__tmp['module'].saveas()
        return status

    def finish(self) -> int:
        """

        Returns:
          int: Status.
        """
        status = -1
        self.close_log()
        # clean_folder
        return status

    def _time(self) -> dict:
        """

        Returns:
          int: Status.
        """
        # Class self.__conf['time']
        time = self.__conf['time']

        if self.__status['code'] == 0:
            now = datetime.datetime.now()

            self.__conf['time']['start'] = now
            self.__conf['time']['now'] = now
            self.__conf['time']['end'] = now
        return time

    def _account(self) -> dict:
        """

        Returns:
          dict: account.
        """
        # Class self.__conf['account'] <- User.account
        account = self.__conf['account']

        if self.__status['code'] == 0:
            account['name'] = self._User__conf['account']['name']
            account['data'] = self._User__conf['account']['data']

            self.__conf['account']['name'] = account['name']
            self.__conf['account']['data'] = account['data']
        return account

    def _product(self) -> dict:
        """

        Returns:
          dict: product.
        """
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

    def _folder(self) -> dict:
        folder = self.__conf['folder']

        # Define folder
        if self.__status['code'] == 0:
            workspace = self.__conf['path']

            variable = self.__conf['product']['variable']

            #  _parameter_ / _resolution_ / _variable_ / _product_ \_ _version_
            path = os.path.join(workspace, variable)
            folder = {
                'r': os.path.join(path, 'remote'),
                't': os.path.join(path, 'temporary'),
                'l': os.path.join(path, 'download')
            }

            for key, value in folder.items():
                if not os.path.exists(value):
                    os.makedirs(value)

            self.__conf['folder'] = folder
        return folder

    def clean_folder(self, name):
        statue = 1

        # os.chdir(output_folder)
        # re = glob.glob("*.dat")
        # for f in re:
        #     os.remove(os.path.join(output_folder, f))
        return statue

    def _log(self) -> dict:
        """

        Returns:
          dict: log.
        """
        # Class self.__conf['log']
        status = -1
        log = self.__conf['log']

        if self.__status['code'] == 0:
            path = self.__conf['path']
            time = self.__conf['time']['start']
            time_str = time.strftime('%Y-%m-%d %H:%M:%S.%f')

            fname = log['name']
            file = os.path.join(path, fname)

            # -1: not found, 0: closed, 1: opened
            fp = self.create_log(file)

            self.__conf['log']['fname'] = fname
            self.__conf['log']['file'] = file
            self.__conf['log']['fp'] = fp
            self.__conf['log']['status'] = status
        return log

    def create_log(self, file):
        time = datetime.datetime.now()
        time_str = time.strftime('%Y-%m-%d %H:%M:%S.%f')
        self.__conf['time']['now'] = time

        print('Create log file: {f}'.format(f=file))
        txt = '{t}: IHEWAcollect created.'.format(t=time_str)
        fp = open(file, 'w+')
        fp.write('{}\n'.format(txt))

        return fp

    def close_log(self):
        time = datetime.datetime.now()
        time_str = time.strftime('%Y-%m-%d %H:%M:%S.%f')
        self.__conf['time']['now'] = time

        file = self.__conf['log']['file']
        fp = self.__conf['log']['fp']

        print('Close log file: {f}'.format(f=file))
        txt = '{t}: IHEWAcollect finished.'.format(t=time_str)
        fp.write('{}\n'.format(txt))
        fp.close()
        self.__conf['log']['fp'] = None

    def _downloader(self) -> dict:
        # ['FTP', 'SFTP', 'HTTP', 'TDS', 'API']
        downloader = self.__conf['downloader']

        if self.__status['code'] == 0:
            module_obj = None
            product = self._Base__conf['product']['data']

            version = self.__conf['product']['version']
            parameter = self.__conf['product']['parameter']
            resolution = self.__conf['product']['resolution']

            url = product[version][parameter][resolution]['url']
            protocol = product[version][parameter][resolution]['protocol']
            method = product[version][parameter][resolution]['method']
            freq = product[version][parameter][resolution]['freq']

            downloader['url'] = url
            downloader['protocol'] = protocol
            downloader['method'] = method.split('.')
            downloader['freq'] = freq
            # Load module
            # variable = self.__conf['product']['data']
            if protocol == 'FTP':
                downloader['name'] = 'ftplib'
            elif protocol == 'SFTP':
                downloader['name'] = 'paramiko'
            elif protocol == 'HTTP':
                downloader['name'] = 'requests'
            elif protocol == 'HTTPS':
                downloader['name'] = 'requests'
            elif protocol == 'API':
                downloader['name'] = 'api'
            else:
                downloader['name'] = ''
                raise IHEClassInitError('Download') from None

        self.__conf['downloader']['name'] = downloader['name']
        self.__conf['downloader']['url'] = downloader['url']
        self.__conf['downloader']['protocol'] = downloader['protocol']
        self.__conf['downloader']['method'] = downloader['method']
        self.__conf['downloader']['freq'] = downloader['freq']
        self.__conf['downloader']['data'] = downloader['data']
        return downloader

    def _template(self) -> dict:
        """

        Returns:
          dict: template.
        """
        # Class self.__tmp <- Base.product
        template = self.__tmp

        if self.__status['code'] == 0:
            module_obj = None
            template['name'] = self._Base__conf['product']['data']['template']

            # Load module
            try:
                # def template_load(self) -> dict:
                module_obj = \
                    importlib.import_module('.{m}'.format(m=template['name']),
                                            'IHEWAcollect.templates')
                print('Loaded module from IHEWAcollect'
                      '.{m}'.format(m=template['name']))
            except ImportError:
                module_obj = \
                    importlib.import_module('src.IHEWAcollect.templates'
                                            '.{m}'.format(m=template['name']))
                print('Loaded module from src.IHEWAcollect'
                      '.{m}'.format(m=template['name']))
            finally:
                # def template_init(self) -> dict:
                if module_obj is not None:
                    template['module'] = module_obj.Template(self.__status, self.__conf)
                else:
                    template['module'] = None
                    raise IHEClassInitError('Download') from None

            self.__tmp['name'] = template['name']
            self.__tmp['module'] = template['module']
        return template


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
    version = 'v1'
    parameter = 'evapotranspiration'
    resolution = 'daily'
    variable = 'ETA'

    # product = 'ECMWF'

    # product = 'TRMM'
    # version = 'v7'
    # parameter = 'precipitation'
    # resolution = 'monthly'
    # variable = 'PCP'

    download = Download(workspace=path,
                        product=product,
                        version=version,
                        parameter=parameter,
                        resolution=resolution,
                        variable=variable,
                        bbox={
                            'n':  1.0,
                            's': -1.0,
                            'w': -1.0,
                            'e': 1.0
                        },
                        period={
                            's': datetime.datetime(2000, 1, 1),
                            'e': datetime.datetime(2000, 3, 31)
                        },
                        is_status=False)

    # # # Base attributes
    # # print('\ndownload._Base__conf\n=====')
    # # pprint(download._Base__conf)
    #
    # # User attributes
    # print('\ndownload._User__conf\n=====')
    # pprint(download._User__conf['account'])
    #
    # # # GIS attributes
    # # print('\ndownload._GIS__conf:\n=====')
    # # pprint(download._GIS__conf)
    #
    # # # Dtime attributes
    # # print('\ndownload._Dtime__conf:\n=====')
    # # pprint(download._Dtime__conf)
    #
    # # Download attributes
    # print('\ndownload._Download__conf()\n=====')
    # # pprint(download._Download__conf.keys())
    # pprint(download._Download__conf)
    #
    # # Download methods
    # print('\ndownload.get_status()\n=====')
    # pprint(download.get_status())


if __name__ == "__main__":
    main()
