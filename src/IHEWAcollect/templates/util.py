# -*- coding: utf-8 -*-
"""
**utils**

`Restrictions`

The data and this python file may not be distributed to others without
permission of the WA+ team.

`Description`

Utilities for IHEWAcollect template modules.
"""
import os

import gzip
import zipfile
import tarfile

# import datetime
import numpy as np


try:
    from .exception import \
        IHEStringError, IHETypeError, IHEKeyError, IHEFileError
except ImportError:
    from IHEWAcollect.base.exception \
        import IHEStringError, IHETypeError, IHEKeyError, IHEFileError


class Extract(object):
    """This util.Extract class

    File pre-process, extract.

    Args:
      is_clean (bool): Is to clean all files in the folder.
    """
    __status = {
        'messages': {
            0: 'S: WA.Extract  {f:>20} : status {c}, {m}',
            1: 'E: WA.Extract  {f:>20} : status {c}: {m}',
            2: 'W: WA.Extract  {f:>20} : status {c}: {m}',
        },
        'code': 0,
        'message': '',
        'is_print': True
    }

    __conf = {
        'file': {
            'i': '',
            'o': ''
        },
        'folder': {
            'i': '',
            'o': ''
        }
    }

    def __init__(self, file, folder, is_print):
        self.__status['is_print'] = is_print
        self.__conf['file'] = file
        self.__conf['folder'] = folder

    def zip(self):
        """Extract zip file

        This function extract zip file.

        Args:
          file (str): Name of the file that must be unzipped.
          outfile (str): Directory where the unzipped data must be stored.
        """
        z = zipfile.ZipFile(self.__conf['file']['i'], 'r')
        z.extractall(self.__conf['folder']['o'])
        z.close()

    def gz(self):
        """Extract gz file

        This function extract gz file.

        Args:
          file (str): Name of the file that must be unzipped.
          outfile (str): Directory where the unzipped data must be stored.
        """
        with gzip.GzipFile(self.__conf['file']['i'], 'rb') as zf:
            file_content = zf.read()
            save_file_content = open(self.__conf['file']['o'], 'wb')
            save_file_content.write(file_content)
        save_file_content.close()
        zf.close()
        # os.remove(ifile)

    def tar(self):
        """Extract tar file

        This function extract tar file.

        Args:
          file (str): Name of the file that must be unzipped.
          outfile (str): Directory where the unzipped data must be stored.
        """
        os.chdir(self.__conf['folder']['o'])
        tar = tarfile.open(self.__conf['file']['i'], "r:gz")
        tar.extractall()
        tar.close()


class Plot(object):
    """This util.Plot class

    File post-process, save or show.

    Args:
      is_save (bool): Is to clean all files in the folder.
    """
    __status = {
        'messages': {
            0: 'S: WA.Plot     {f:>20} : status {c}, {m}',
            1: 'E: WA.Plot     {f:>20} : status {c}: {m}',
            2: 'W: WA.Plot     {f:>20} : status {c}: {m}',
        },
        'code': 0,
        'message': '',
        'is_print': True
    }

    __conf = {
        'name': '',
        'data': np.ndarray,
        'file': {
            'i': '',
            'o': ''
        },
        'folder': {
            'i': '',
            'o': ''
        },
        'is_save': False,
        'is_show': False
    }

    def __init__(self, data, file, folder, is_print, is_save, is_show):
        self.__status['is_print'] = is_print
        self.__conf['data'] = data
        self.__conf['file'] = file
        self.__conf['folder'] = folder
        self.__conf['is_save'] = is_save
        self.__conf['is_show'] = is_show


class Waitbar(object):
    """This util.Waitbar class

    Waitbar on the cmd window.

    Args:
      is_save (bool): Is to clean all files in the folder.
    """
    __status = {
        'messages': {
            0: 'S: WA.Waitbar  {f:>20} : status {c}, {m}',
            1: 'E: WA.Waitbar  {f:>20} : status {c}: {m}',
            2: 'W: WA.Waitbar  {f:>20} : status {c}: {m}',
        },
        'code': 0,
        'message': '',
        'is_print': True
    }

    __conf = {
        'statue': {
            's': 0,
            'e': 100,
            'i': 0,
        }
    }

    def __init__(self, is_print):
        self.__status['is_print'] = is_print


class Log(object):
    __conf = {}
    data = {}

    def __init__(self, config, **kwargs):
        self.__conf = config

    def write(self, time, msg=''):
        txt = '{t}: {msg}'.format(t=time.strftime('%Y-%m-%d %H:%M:%S.%f'), msg=msg)
        self.__conf['fp'].write('{}\n'.format(txt))
