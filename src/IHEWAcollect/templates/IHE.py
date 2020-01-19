# -*- coding: utf-8 -*-
import os

from urllib.parse import urlparse

try:
    from ..base.gis import GIS
    from ..base.dtime import Dtime
    from ..base.util import Log
except ImportError:
    from src.IHEWAcollect.base.gis import GIS
    from src.IHEWAcollect.base.dtime import Dtime
    from src.IHEWAcollect.base.util import Log


class Template(GIS, Dtime):
    status = 'Global status.'

    __status = {}
    __conf = {}
    data = {
        'latlon': None,
        'dtime': None
    }

    def __init__(self, status, config, **kwargs):
        print('Template.__init__()')
        self.__status = status
        self.__conf = config

        # super(IHE, self).__init__(status, config, **kwargs)
        self.gis = GIS(config['path'], status['is_print'], **kwargs)
        self._dtime = Dtime(config['path'], status['is_print'], **kwargs)
        self._log = Log(config['log'])

        # Class GIS
        # self.latlim = self.var['lat']
        # self.lonlim = self.var['lon']
        # self.timlim = self.var['time']

        # Class Dtime

        from pprint import pprint
        print('Template.download()')
        print('\n=> Template.__status')
        pprint(self.__status)
        print('\n=> Template.__conf')
        pprint(self.__conf)

    def _check(self):
        print('Template.check()')

    # def get_url(self):
    #     pass
    #
    # def get_auth(self):
    #     pass
    #
    # def get_rfile(self):
    #     pass
    #
    # def get_tfile(self):
    #     pass
    #
    # def get_lfile(self):
    #     pass

    def download(self):
        print('Template.download()')
        downloader = self.__conf['downloader']
        account = self.__conf['account']['data']
        product = self.__conf['product']['data']
        folder = self.__conf['folder']

        url = urlparse(downloader['url'])
        rdir = ''
        fname = ''
        file = ''
        if self.__status['code'] == 0:
            from ftplib import FTP, all_errors

            username = account['username']
            password = account['password']
            # apitoken = account['apitoken']

            dfmt = product['dfmt']
            if dfmt is None:
                rdir = product['dir']
            else:
                if 'dtime' in dfmt:
                    rdir = product['dir'].format(
                        dtime=self.__conf['time']['now'])

            rfmt = product['rfmt']
            if rfmt is None:
                fname = product['fname']['r']
            else:
                if 'dtime' in rfmt:
                    fname = product['fname']['r'].format(
                        dtime=self.__conf['time']['now'])

            # print(url, dir, file)
            file = os.path.join(folder['r'], fname)
            msg = 'Downloading "{f}"'.format(f=fname)
            self._log.write(self.__conf['time']['now'], msg=msg)

            try:
                ftp = FTP(url.netloc)
                ftp.login(username, password)
                ftp.cwd(rdir)
            except all_errors as err:
                print(err)
                self._log.write(self.__conf['time']['now'], msg=str(err))
            else:
                fp = open(file, 'wb')
                try:
                    ftp.retrbinary("RETR " + fname, fp.write)
                except all_errors as err:
                    print(err)
                    self._log.write(self.__conf['time']['now'], msg=str(err))

            # downloader['module'] = ftp
            # downloader['module'] = module_obj.Template(self.__status, self.__conf)

    def convert(self):
        print('Template.convert()')

    def saveas(self):
        print('Template.saveas()')
