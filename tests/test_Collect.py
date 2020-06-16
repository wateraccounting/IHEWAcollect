# -*- coding: utf-8 -*-
"""
"""
# General modules
import os

# IHEWAcollect Modules
import IHEWAcollect
import numpy as np
import pandas as pd

# import sys

# import pytest


# from IHEWAcollect.base.user import User
# from IHEWAcollect.templates.gis import GIS
# from IHEWAcollect.templates.dtime import Dtime

__author__ = "Quan Pan"
__copyright__ = "Quan Pan"
__license__ = "apache"

__path = os.path.dirname(os.path.realpath(__file__))
__path_data = os.path.join(__path, 'data')


# def test_credential():
#     path = __path_data
#     file_org = 'config-test.yml'
#     file_enc = 'config-test.yml-encrypted'
#     password = 'WaterAccounting'
#
#     key1 = credential.get_key(password)
#     key2 = credential.encrypt_cfg(path, file_org, password)
#     conf = credential.decrypt_cfg(path, file_enc, password)
#
#     assert len(key1) == 44
#     assert len(key2) == 44
#     assert key1.decode('utf8') == key2.decode('utf8')
#     assert type(conf) == str
#
#     # credential.encrypt_cfg('', 'config.yml', 'WaterAccounting')
#     # with pytest.raises(FileNotFoundError, match=r".* No .*"):
#     #     credential.encrypt_cfg('', 'config.yml', 'WaterAccounting')


# https://docs.travis-ci.com/user/common-build-problems/#ftpsmtpother-protocol-do-not-work
def test_CFSR():
    # path = os.path.join(__path_data, 'download')
    path = __path

    test_freq = 'D'
    test_units = 'W.m2'
    test_args = {
        '1a': {
            'product': 'CFSR',
            'version': 'v1',
            'parameter': 'radiation',
            'resolution': 'daily',
            'variable': 'dlwsfc',
            'bbox': {
                'w': -19.0,
                'n': 38.0,
                'e': 55.0,
                's': -35.0
            },
            'period': {
                's': '2007-01-01',
                'e': '2007-01-01'
            },
            'nodata': -9999
        }
    }

    for key, value in test_args.items():
        IHEWAcollect.Download(workspace=path,
                              product=value['product'],
                              version=value['version'],
                              parameter=value['parameter'],
                              resolution=value['resolution'],
                              variable=value['variable'],
                              bbox=value['bbox'],
                              period=value['period'],
                              nodata=value['nodata'],
                              is_status=True,
                              is_save_temp=True,
                              is_save_remote=True)

        date_s = pd.Timestamp(value['period']['s'])
        date_e = pd.Timestamp(value['period']['e'])
        date_dates = pd.date_range(date_s, date_e, freq=test_freq)
        ndates = len(date_dates)

        local_path = os.path.join(path,
                                  'IHEWAcollect',
                                  value['variable'],
                                  'download')
        test_fname = '{p}_{v}_{u}_{f}'.format(
            p=value['product'],
            v=value['version'],
            u=test_units,
            f=test_freq
        )
        fnames = os.listdir(local_path)
        local_files = []
        for fname in fnames:
            print(fname)
            if test_fname in fname:
                file = os.path.join(local_path, fname)
                if np.ceil(os.stat(file).st_size / 1024) > 0:
                    local_files.append(file)
        nfiles = len(local_files)

        assert ndates == nfiles
