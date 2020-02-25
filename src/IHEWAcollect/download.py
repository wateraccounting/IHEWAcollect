# -*- coding: utf-8 -*-
"""
**Download**

Before use this module, create ``accounts.yml`` file.
And edit account information in the file.
"""
# import shutil
import datetime
import importlib
import inspect
import os
# import sys

try:
    # IHEClassInitError, IHEStringError, IHETypeError, IHEKeyError, IHEFileError
    from .base.exception import IHEClassInitError,\
        IHEKeyError
except ImportError:
    from IHEWAcollect.base.exception import IHEClassInitError,\
        IHEKeyError

try:
    from .base.user import User
except ImportError:
    from IHEWAcollect.base.user import User


class Download(User):
    """Download class

    After initialise the class, data downloading will automatically start.

    Args:
        workspace (str): Directory to accounts.yml.
        product (str): Product name.
        version (str): Version name.
        parameter (str): Parameter name.
        resolution (str): Resolution name.
        variable (str): Variable name.
        bbox (dict): Spatial range, {'w':, 's':, 'e':, 'n':}.
        period (dict): Time range, {'s':, 'e':}.
        nodata (int): -9999.
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
            self._download_init()

            self._download_prepare()
            self._download_start()
            self._download_finish()

            self.__status['message'] = ''
        else:
            raise IHEClassInitError('Download') from None

    def _set_status(self, fun='', prt=False, ext=''):
        """Set status

        Args:
            fun (str): Function name.
            prt (bool): Is to print on screen?
            ext (str): Extra message.
        """
        self.status = self._status(self.__status['messages'],
                                   self.__status['code'],
                                   fun, prt, ext)

    def _download_init(self) -> int:
        """

        Returns:
            int: Status.
        """
        status = -1
        self._time()
        self._account()
        self._product()
        return status

    def _download_prepare(self) -> int:
        """

        Returns:
            int: Status.
        """
        status = -1
        self._folder()
        self._log()
        self._template()
        # _folder_clean
        return status

    def _download_start(self) -> int:
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

    def _download_finish(self) -> int:
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
            # time_str = time.strftime('%Y-%m-%d %H:%M:%S.%f')

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

        print('Create log file "{f}"'.format(f=file))
        txt = '{t}: IHEWAcollect'.format(t=time_str)

        fp = open(file, 'w+')
        fp.write('{}\n'.format(txt))
        for key, value in self.__conf['product'].items():
            if key != 'data':
                fp.write('{:>26s}: {}\n'.format(key, str(value)))

        return fp

    def _log_close(self):
        time = datetime.datetime.now()
        time_str = time.strftime('%Y-%m-%d %H:%M:%S.%f')
        self.__conf['time']['now'] = time

        file = self.__conf['log']['file']
        fp = self.__conf['log']['fp']

        print('Close log file "{f}"'.format(f=file))
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
            module_name_base = '{tmp}.{prod}'.format(
                tmp=self._Base__conf['product']['data']['template'],
                prod=product['name'])

            # Load module
            # module_obj = None
            module_name = template['name']
            module_obj = template['module']
            if module_obj is None:
                is_reload_module = False
            else:
                if module_name == module_name_base:
                    is_reload_module = True
                else:
                    is_reload_module = False
            template['name'] = module_name_base

            if is_reload_module:
                try:
                    module_obj = importlib.reload(module_obj)
                except ImportError:
                    raise IHEClassInitError('Templates') from None
                else:
                    template['module'] = module_obj
                    print('Reloaded module'
                          '.{p}.{m}'.format(p=product['template'],
                                            m=product['name']))
            else:
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
                    else:
                        raise IHEClassInitError('Templates') from None

            self.__tmp['name'] = template['name']
            self.__tmp['module'] = template['module']
        return template

    def get_products(self) -> dict:
        """Get details of all products

        Returns:
            dict: Products data.
        """
        products = self._Base__conf['data']['products']

        # import pandas as pd
        # df_products = pd.DataFrame.from_dict(products)
        # print(df_products)

        str_col = ['id',
                   'product',
                   'account',
                   'protocol',
                   'version',
                   'parameter',
                   'resolution',
                   'variable',
                   'lat_s', 'lat_n', 'lat_r',
                   'lon_w', 'lon_e', 'lon_r',
                   'time_s', 'time_e']

        str_size = 10
        print('')

        # str_fmt = ''
        # str_fmt_cel = '{col[%d]:>' + str(str_size) + '}%s'
        # for icol in range(len(str_col)):
        #     str_fmt += str_fmt_cel % (icol, ', ')
        # str_fmt += ''
        # print(str_fmt.format(col=str_col))

        # ================= #
        # ReStructured Text #
        # ================= #
        # str_tmp = ''
        # for icol in range(len(str_col)):
        #     str_tmp += '+{sep:->' + str(str_size + 2) + 's}'
        # str_tmp += '+'
        # print(str_tmp.format(sep=''))

        # str_tmp = ''
        # str_tmp_cel = '| {col[%d]:>' + str(str_size) + '}%s'
        # for icol in range(len(str_col)):
        #     str_tmp += str_tmp_cel % (icol, ' ')
        # str_tmp += '|'
        # print(str_tmp.format(col=str_col))

        # str_tmp = ''
        # for icol in range(len(str_col)):
        #     str_tmp += '+{sep:=>' + str(str_size + 2) + 's}'
        # str_tmp += '+'
        # print(str_tmp.format(sep=''))

        # ============================= #
        # .. csv-table:: Product Detail #
        # ============================= #
        str_tmp = '.. csv-table:: Product Detail'
        print(str_tmp)

        str_tmp = '    :header: '
        str_tmp_cel = '"{col[%d]}"%s'
        for icol in range(len(str_col) - 1):
            str_tmp += str_tmp_cel % (icol, ',')
        str_tmp += str_tmp_cel % (len(str_col) - 1, '')
        print(str_tmp.format(col=str_col))

        str_tmp = '    :widths: '
        str_tmp_cel = '%d%s'
        for icol in range(len(str_col) - 1):
            str_tmp += str_tmp_cel % (str_size, ',')
        str_tmp += str_tmp_cel % (str_size, '\n')
        print(str_tmp)

        i = 0
        for pd_n, pd_d in products.items():
            pd_a = pd_d['account']

            for pd_ver_n, pd_ver_d in pd_d.items():
                if pd_ver_n not in ['account', 'template', 'meta']:

                    for pd_par_n, pd_par_d in pd_ver_d.items():

                        for pd_res_n, pd_res_d in pd_par_d.items():
                            pd_res_d_pro = pd_res_d['protocol']

                            for pd_var_n, pd_var_d in pd_res_d['variables'].items():
                                i += 1

                                # pd_var_d_nam = pd_var_d['name']
                                pd_var_d_lat_s = pd_var_d['lat']['s']
                                pd_var_d_lat_n = pd_var_d['lat']['n']
                                pd_var_d_lat_r = pd_var_d['lat']['r']
                                pd_var_d_lon_w = pd_var_d['lon']['w']
                                pd_var_d_lon_e = pd_var_d['lon']['e']
                                pd_var_d_lon_r = pd_var_d['lon']['r']
                                pd_var_d_tim_s = pd_var_d['time']['s']
                                pd_var_d_tim_e = pd_var_d['time']['e']

                                str_col = [i,
                                           pd_n,
                                           pd_a,
                                           pd_res_d_pro,
                                           pd_ver_n,
                                           pd_par_n,
                                           pd_res_n,
                                           pd_var_n,
                                           pd_var_d_lat_s,
                                           pd_var_d_lat_n,
                                           pd_var_d_lat_r,
                                           pd_var_d_lon_w,
                                           pd_var_d_lon_e,
                                           pd_var_d_lon_r,
                                           pd_var_d_tim_s,
                                           pd_var_d_tim_e]

                                for j in range(len(str_col)):
                                    if isinstance(str_col[j], datetime.datetime):
                                        str_col[j] = str_col[j].strftime('%Y-%m-%d')

                                    if str_col[j] is None:
                                        str_col[j] = 'None'

                                    str_col[j] = str(str_col[j])

                                    if len(str_col[j]) > str_size:
                                        str_col[j] = str_col[j][0:str_size - 1] + '~'

                                # print(str_fmt.format(col=str_col))

                                # ================= #
                                # ReStructured Text
                                # ================= #
                                # str_tmp = ''
                                # for icol in range(len(str_col)):
                                #     str_tmp += '+{sep:->' + str(str_size + 2) + 's}'
                                # str_tmp += '+'
                                # print(str_tmp.format(sep=''))

                                # ============================= #
                                # .. csv-table:: Product Detail #
                                # ============================= #
                                str_tmp = '    '
                                str_tmp_cel = '{col[%d]}%s'
                                for icol in range(len(str_col) - 1):
                                    str_tmp += str_tmp_cel % (icol, ',')
                                str_tmp += str_tmp_cel % (len(str_col) - 1, '')
                                print(str_tmp.format(col=str_col))

        return products


if __name__ == "__main__":
    print('\nDownload\n=====')
    path = os.path.join(
        os.getcwd(),
        os.path.dirname(
            inspect.getfile(
                inspect.currentframe())),
        '../', '../', 'tests'
    )

    test_args = {
        '1a': {
            'product': 'ALEXI',
            'version': 'v1',
            'parameter': 'evapotranspiration',
            'resolution': 'daily',
            'variable': 'ETA',
            'bbox': {
                'w': -19.0,
                'n': 38.0,
                'e': 55.0,
                's': -35.0
            },
            'period': {
                's': '2005-01-01',
                'e': '2005-01-02'
            },
            'nodata': -9999
        }
    }

    # Download __init__
    for key, value in test_args.items():
        print('\n{:>4s}'
              '{:>20s}{:>6s}{:>20s}{:>20s}{:>20s}\n'
              '{:->90s}'.format(key,
                                value['product'],
                                value['version'],
                                value['parameter'],
                                value['resolution'],
                                value['variable'],
                                '-'))

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

    # download.get_products()

    # download.generate_encrypt()

    # import yaml
    # fp = open(os.path.join(path, 'config.yml'), 'w+')
    # yaml.dump(test_args, fp,
    #           default_flow_style=False, sort_keys=False,
    #           allow_unicode=True)
