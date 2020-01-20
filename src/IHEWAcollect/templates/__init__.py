# -*- coding: utf-8 -*-
"""
IHEWAcollect template modules

collect.py Convert_grb2_to_nc() -> Run_command_window("gdal_translate.exe", ...)

"""
# import os
# import importlib
#
# from urllib.parse import urlparse
#
# try:
#     from ..base.exception import IHEClassInitError,\
#         IHEStringError, IHETypeError, IHEKeyError, IHEFileError
# except ImportError:
#     from src.IHEWAcollect.base.exception import IHEClassInitError,\
#         IHEStringError, IHETypeError, IHEKeyError, IHEFileError
#
#
# class Template(GIS, Dtime):
#     status = 'Global status.'
#
#     __status = {}
#     __conf = {}
#     data = {
#         'dir': '',
#         'fname': {
#             'r': '',
#             't': '',
#             'l': ''
#         },
#         'latlon': {
#             'latlim': {
#                 's': 0.0,
#                 'n': 0.0,
#                 'r': 0.0
#             },
#             'lonlim': {
#                 'w': 0.0,
#                 'e': 0.0,
#                 'r': 0.0
#             }
#         },
#         'dtime': {
#             'r': [],
#             'i': 0
#         }
#     }
#
#     def __init__(self, status, config, **kwargs):
#         print('Template.__init__()')
#         self.__status = status
#         self.__conf = config
#
#         # Class GIS
#         self._GIS = GIS(config['path'], config['product'],
#                         status['is_print'], **kwargs)
#         # Class Dtime
#         self._Dtime = Dtime(config['path'], config['product'],
#                             status['is_print'], **kwargs)
#         # Class Log
#         self._Log = Log(config['log'])
#
#         self.get_fname()
#
#         from pprint import pprint
#         print('Template.download()')
#         print('\n=> Template.__status')
#         pprint(self.__status)
#         print('\n=> Template.__conf')
#         pprint(self.__conf)
#         print('\n=> Template.data')
#         pprint(self.data)
#
#     def get_fname(self) -> dict:
#         fname = self.data['fname']
#
#         if self.__status['code'] == 0:
#             product = self.__conf['product']
#
#             fmt = product['data']['fmt']
#             for key in fname:
#                 value = product['data']['fmt'][key]
#
#                 if value is None:
#                     fname[key] = product['data']['fname'][key]
#                 else:
#                     if 'dtime' == value:
#                         fname[key] = product['data']['fname'][key].format(
#                             dtime=self.__conf['time']['now'])
#                     elif 'latlon' == value:
#                         fname[key] = product['data']['fname'][key].format(
#                             dtime=self.__conf['time']['now'])
#                     elif 'dtime.latlon' == value:
#                         fname[key] = product['data']['fname'][key].format(
#                             dtime=self.__conf['time']['now'],
#                             lat=self.__conf['time']['now'],
#                             lon=self.__conf['time']['now'])
#             self.data['fname'] = fname
#         return fname
#
#     # def get_url(self):
#     #     pass
#     #
#     # def get_auth(self):
#     #     pass
#     #
#     # def get_rfile(self):
#     #     pass
#     #
#     # def get_tfile(self):
#     #     pass
#     #
#     # def get_lfile(self):
#     #     pass
#
#     def download(self):
#         status = -1
#         print('Template.download()')
#         downloader = self.__conf['downloader']
#         account = self.__conf['account']
#         product = self.__conf['product']
#         folder = self.__conf['folder']
#
#         url = urlparse(downloader['url'])
#         dir = self.data['dir']
#         fname = self.data['fname']['r']
#         file = ''
#         if self.__status['code'] == 0:
#             from ftplib import FTP, all_errors
#
#             username = account['data']['username']
#             password = account['data']['password']
#             # apitoken = account['data']['apitoken']
#
#             fmt = product['data']['fmt']['d']
#             if fmt is None:
#                 dir = product['data']['dir']
#             else:
#                 if 'dtime' == fmt:
#                     dir = product['data']['dir'].format(
#                         dtime=self.__conf['time']['now'])
#             self.data['dir'] = dir
#
#             # print(url, dir, file)
#             file = os.path.join(folder['r'], fname)
#             msg = 'Downloading "{f}"'.format(f=fname)
#             self._Log.write(self.__conf['time']['now'], msg=msg)
#
#             # try:
#             #     ftp = FTP(url.netloc)
#             #     ftp.login(username, password)
#             #     ftp.cwd(dir)
#             # except all_errors as err:
#             #     print(err)
#             #     self._Log.write(self.__conf['time']['now'], msg=str(err))
#             # else:
#             #     fp = open(file, 'wb')
#             #     try:
#             #         ftp.retrbinary("RETR " + fname, fp.write)
#             #         fp.close()
#             #     except all_errors as err:
#             #         print(err)
#             #         self._Log.write(self.__conf['time']['now'], msg=str(err))
#             #         fp.close()
#             #         os.remove(file)
#         return status
#     #
#     # def convert(self):
#     #     print('Template.convert()')
#     #
#     # def saveas(self):
#     #     print('Template.saveas()')
