# -*- coding: utf-8 -*-
"""
**utils**

Utilities for IHEWAcollect template modules.
"""
import inspect
import os
import sys
# import shutil
# import datetime

import gzip
import tarfile
import zipfile

import numpy as np
import pandas as pd

try:
    from .exception import \
        IHEStringError, IHETypeError, IHEKeyError, IHEFileError
except ImportError:
    from IHEWAcollect.base.exception \
        import IHEStringError, IHETypeError, IHEKeyError, IHEFileError


class Extract(object):
    """Extract class

    File pre-process, extract.

    Args:
        file (str): File.
        folder (str): Folder.
        is_print (bool): Is to print status message.
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
        """Class instantiation
        """
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
    """Plot class

    File post-process, save or show.

    Args:
        data
        file
        folder
        is_print (bool): Is to print status message.
        is_save (bool): Is to save files in the folder.
        is_show (bool): Is to show files in the folder.
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
    """Waitbar class

    Waitbar on the cmd window.

    Args:
        is_print (bool): Is to print status message.
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
        """Class instantiation
        """
        self.__status['is_print'] = is_print

    @staticmethod
    def wait_bar(i, total,
                 prefix='', suffix='',
                 decimals=1, length=100, fill='█'):
        """Wait Bar Console

        This function will print a waitbar in the console

        Args:
            i (int): Iteration number.
            total (int): Total iterations.
            prefix (str): Prefix name of bar.
            suffix (str): Suffix name of bar.
            decimals (int): Decimal of the wait bar.
            length (int): Width of the wait bar.
            fill (str): Bar fill.
        """
        # Adjust when it is a linux computer
        if os.name == 'posix' and total == 0:
            total = 0.0001

        percent = ('{0:.' + str(decimals) + 'f}').format(100 *
                                                         (i / float(total)))
        filled = int(length * i // total)
        bar = fill * filled + '-' * (length - filled)

        sys.stdout.write('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix))
        sys.stdout.flush()

        if i == total:
            print()


class Log(object):
    """Log class

    Write message to log file.

    Args:
        config (dict): Is to print status message.
    """
    __conf = {}
    data = {}

    def __init__(self, config, **kwargs):
        self.__conf = config

    def write(self, time, msg=''):
        txt = '{t}: {msg}'.format(t=time.strftime('%Y-%m-%d %H:%M:%S.%f'), msg=msg)
        self.__conf['fp'].write('{}\n'.format(txt))
