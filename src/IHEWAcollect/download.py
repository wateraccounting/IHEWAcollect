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
import sys
import inspect
import importlib

# import shutil
# import yaml
import datetime

try:
    from .base.exception import IHEClassInitError,\
        IHEStringError, IHETypeError, IHEKeyError, IHEFileError
except ImportError:
    from IHEWAcollect.base.exception import IHEClassInitError,\
        IHEStringError, IHETypeError, IHEKeyError, IHEFileError

try:
    from .base.user import User
except ImportError:
    from IHEWAcollect.base.user import User


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
      NaN (int): -9999.
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
            'bbox': {},
            'period': {},
            'nodata': -9999,
            'template': '',
            'url': '',
            'protocol': '',
            'method': '',
            'freq': '',
            'data': {}
        },
        'folder': {
            'r': '',
            't': '',
            'l': ''
        },
        'log': {
            'name': 'log.{var}.{res}.{prod}.txt',
            'file': '{path}/log-.txt',
            'fp': None,
            'status': -1,  # -1: not found, 0: closed, 1: opened
        }
    }
    __tmp = {
        'name': '',
        'module': None,
        'data': {}
    }

    def __init__(self, workspace='',
                 product='', version='', parameter='', resolution='', variable='',
                 bbox={}, period={}, nodata=-9999,
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
        self.__conf['product']['nodata'] = nodata

        # super(Download, self).__init__(**kwargs)
        if self.__status['code'] == 0:
            User.__init__(self, workspace, product, is_status, **kwargs)
        else:
            raise IHEClassInitError('Download') from None

        # Class Download
        if self.__status['code'] == 0:
            self.init()

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

    def init(self) -> int:
        """

        Returns:
          int: Status.
        """
        status = -1
        self._time()
        self._account()
        self._product()
        return status

    def prepare(self) -> int:
        """

        Returns:
          int: Status.
        """
        status = -1
        self._folder()
        self._log()
        self._template()
        return status

    def start(self) -> int:
        """

        Returns:
          int: Status.
        """
        status = -1
        self.__tmp['module'].DownloadData(self.__status, self.__conf)
        # self.__tmp['module'].download()
        # self.__tmp['module'].convert()
        # self.__tmp['module'].saveas()
        return status

    def finish(self) -> int:
        """

        Returns:
          int: Status.
        """
        status = -1
        self._log_close()
        # _folder_clean
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
            product['name'] = \
                self._Base__conf['product']['name']
            product['data'] = \
                self._Base__conf['product']['data']
            product['template'] = \
                self._Base__conf['product']['data'][
                    'template']
            product['url'] = \
                self._Base__conf['product']['data'][
                    version][parameter][resolution]['url']
            product['protocol'] = \
                self._Base__conf['product']['data'][
                    version][parameter][resolution]['protocol']
            product['method'] = \
                self._Base__conf['product']['data'][
                    version][parameter][resolution]['method']
            product['freq'] = \
                self._Base__conf['product']['data'][
                    version][parameter][resolution]['freq']

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

    def _folder_clean(self, name):
        statue = 1

        # shutil

        # re = glob.glob(os.path.join(folder['r'], '*'))
        # for f in re:
        #     os.remove(os.path.join(folder['r'], f))
        return statue

    def _log(self) -> dict:
        """

        Returns:
          dict: log.
        """
        # Class self.__conf['log']
        status = -1
        log = self.__conf['log']
        product = self.__conf['product']['name']
        resolution = self.__conf['product']['resolution']
        variable = self.__conf['product']['variable']

        if self.__status['code'] == 0:
            path = self.__conf['path']
            time = self.__conf['time']['start']
            time_str = time.strftime('%Y-%m-%d %H:%M:%S.%f')

            fname = log['name'].format(prod=product, var=variable, res=resolution)
            file = os.path.join(path, fname)

            # -1: not found, 0: closed, 1: opened
            fp = self._log_create(file)

            self.__conf['log']['fname'] = fname
            self.__conf['log']['file'] = file
            self.__conf['log']['fp'] = fp
            self.__conf['log']['status'] = status
        return log

    def _log_create(self, file):
        time = datetime.datetime.now()
        time_str = time.strftime('%Y-%m-%d %H:%M:%S.%f')
        self.__conf['time']['now'] = time

        print('Create log file: {f}'.format(f=file))
        txt = '{t}: IHEWAcollect'.format(t=time_str)

        fp = open(file, 'w+')
        fp.write('{}\n'.format(txt))
        for key, value in self.__conf['product'].items():
            if key is not 'data':
                fp.write('{:>26s}: {}\n'.format(key, str(value)))

        return fp

    def _log_close(self):
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

    def _template(self) -> dict:
        """

        Returns:
          dict: template.
        """
        # Class self.__tmp <- Base.product
        template = self.__tmp

        if self.__status['code'] == 0:
            product = self.__conf['product']
            template['name'] = self._Base__conf['product']['data']['template']

            # Load module
            # module_obj = None

            module_obj = template['module']
            if module_obj is None:
                try:
                    # def template_load(self) -> dict:
                    module_obj = \
                        importlib.import_module('IHEWAcollect.templates'
                                                '.{p}.{m}'.format(p=product['template'],
                                                                  m=product['name']))
                    print('Loaded module from IHEWAcollect.templates'
                          '.{p}.{m}'.format(p=product['template'],
                                            m=product['name']))
                except ImportError:
                    module_obj = \
                        importlib.import_module('IHEWAcollect.templates'
                                                '.{p}.{m}'.format(p=product['template'],
                                                                  m=product['name']))
                    print('Loaded module from IHEWAcollect.templates'
                          '.{p}.{m}'.format(p=product['template'],
                                            m=product['name']))
                finally:
                    # def template_init(self) -> dict:
                    if module_obj is not None:
                        template['module'] = module_obj
                        # module_obj.DownloadData(self.__status, self.__conf)
                    else:
                        template['module'] = None
                        raise IHEClassInitError('Templates') from None
            else:
                try:
                    module_obj = importlib.reload(module_obj)
                except ImportError:
                    template['module'] = None
                    raise IHEClassInitError('Templates') from None

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

    test_args = {
        '1': {
            'product': 'ALEXI',
            'version': 'v1',
            'parameter': 'evapotranspiration',
            'resolution': 'daily',
            'variable': 'ETA',
            'bbox': {
                'w': -19.0,
                's': -35.0,
                'e': 55.0,
                'n': 38.0
            },
            'period': {
                's': '2005-01-01',
                'e': '2005-01-02'
            },
            'nodata': -9999
        },
        '2': {
            'product': 'ALEXI',
            'version': 'v1',
            'parameter': 'evapotranspiration',
            'resolution': 'weekly',
            'variable': 'ETA',
            'bbox': {
                'w': -19.0,
                's': -35.0,
                'e': 55.0,
                'n': 38.0
            },
            'period': {
                's': '2005-01-01',
                'e': '2005-01-15'
            },
            'nodata': -9999
        },
        '3': {
            'product': 'ASCAT',
            'version': 'v3.1.1',
            'parameter': 'soil_water_index',
            'resolution': 'daily',
            'variable': 'SWI_010',
            'bbox': {
                'w': -19.0,
                's': -35.0,
                'e': 55.0,
                'n': 38.0
            },
            'period': {
                's': '2005-01-01',
                'e': '2005-01-02'
            },
            'nodata': -9999
        },
    }

    # # Caution:
    # # dec_jpeg2000: Unable to open JPEG2000 image within GRIB file.
    # # Docker, pass!
    # product = 'CFSR'
    # version = 'v1'
    # parameter = 'radiation'
    # resolution = 'daily'
    # variable = 'dlwsfc'
    # bbox = {
    #     'w': -19.0,
    #     's': -35.0,
    #     'e': 55.0,
    #     'n': 38.0
    # }
    # period = {
    #     's': '2007-01-01',
    #     'e': '2007-01-02'
    # }
    # nodata = -9999

    # product = 'CHIRPS'
    # version = 'v2.0'
    # parameter = 'precipitation'
    # resolution = 'daily'
    # # resolution = 'monthly'
    # variable = 'PCP'
    # bbox = {
    #     'w': -19.0,
    #     's': -35.0,
    #     'e': 55.0,
    #     'n': 38.0
    # }
    # period = {
    #     's': '2007-01-01',
    #     'e': '2007-01-31'
    # }
    # nodata = -9999

    # product = 'CMRSET'
    # version = 'v1'
    # parameter = 'evapotranspiration'
    # resolution = 'monthly'
    # variable = 'ETA'
    # bbox = {
    #     'w': -19.0,
    #     's': -35.0,
    #     'e': 55.0,
    #     'n': 38.0
    # }
    # period = {
    #     's': '2007-01-01',
    #     'e': '2007-01-31'
    # }
    # nodata = -9999

    # TODO, 20200120, QPan, DEM, replace some values, and re-design base.yml
    # product = 'DEM'
    # version = 'v1'
    # parameter = 'DEM'
    # resolution = '30s'
    # variable = 'af'
    # bbox = {
    #     'w': -19.0,
    #     's': -35.0,
    #     'e': 55.0,
    #     'n': 38.0
    # }
    # period = {
    #     's': '',
    #     'e': ''
    # }
    # nodata = -9999

    # TODO, ECMWF
    # product = ''

    # Caution:
    # # A 69618 pixels x 29007 lines x 1 bands Float32 image would be larger than 4GB
    # # but this is the largest size a TIFF can be, and BigTIFF is unavailable.
    # Docker, pass!
    # product = 'ETmonitor'
    # version = 'v1'
    # parameter = 'evapotranspiration'
    # resolution = 'monthly'
    # variable = 'ETA'
    # # variable = 'ETP'
    # bbox = {
    #     'w': -19.0,
    #     's': -35.0,
    #     'e': 55.0,
    #     'n': 38.0
    # }
    # period = {
    #     's': '2008-01-01',
    #     'e': '2008-01-31'
    # }
    # nodata = -9999

    # product = 'FEWS'
    # version = 'v4'
    # parameter = 'evapotranspiration'
    # resolution = 'daily'
    # variable = 'ETP'
    # bbox = {
    #     'w': -19.0,
    #     's': -35.0,
    #     'e': 55.0,
    #     'n': 38.0
    # }
    # period = {
    #     's': '2008-01-01',
    #     'e': '2008-01-31'
    # }
    # nodata = -9999

    # TODO, 20200120, QPan, GLDAS, change code of download from "requested text" to "NetCDF"
    # product = 'GLDAS'
    # version = 'v2.1'
    # parameter = 'evapotranspiration'
    # resolution = 'three_hourly'
    # variable = 'ET'
    # bbox = {
    #     'w': -19.0,
    #     's': -35.0,
    #     'e': 55.0,
    #     'n': 38.0
    # }
    # period = {
    #     's': '2008-01-01',
    #     'e': '2008-01-31'
    # }
    # nodata = -9999

    # TODO, 20200120, QPan, GLEAM, replace some values
    # product = 'GLEAM'
    # version = 'v3.3a'
    # parameter = 'evapotranspiration'
    # resolution = 'daily'
    # variable = 'ET'
    # bbox = {
    #     'w': -19.0,
    #     's': -35.0,
    #     'e': 55.0,
    #     'n': 38.0
    # }
    # period = {
    #     's': '2008-01-01',
    #     'e': '2008-01-31'
    # }
    # nodata = -9999

    # TODO, GPM
    # product = 'GPM'
    # version = 'v6'
    # parameter = 'precipitation'
    # resolution = 'daily'
    # variable = 'PCP'
    # bbox = {
    #     'w': -19.0,
    #     's': -35.0,
    #     'e': 55.0,
    #     'n': 38.0
    # }
    # period = {
    #     's': '2008-01-01',
    #     'e': '2008-01-31'
    # }
    # nodata = -9999

    # product = 'TRMM'
    # version = 'v7'
    # parameter = 'precipitation'
    # resolution = 'monthly'
    # variable = 'PCP'

    for key, value in test_args.items():
        print('\ntest case {:>10s}\n-----'.format(key))

        download = Download(workspace=path,
                            product=value['product'],
                            version=value['version'],
                            parameter=value['parameter'],
                            resolution=value['resolution'],
                            variable=value['variable'],
                            bbox=value['bbox'],
                            period=value['period'],
                            nodata=value['nodata'],
                            is_status=False)


if __name__ == "__main__":
    main()
