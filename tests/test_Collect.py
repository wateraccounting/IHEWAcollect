# -*- coding: utf-8 -*-
"""
"""
import pytest

# General modules
import os

# import numpy as np

# IHEWAcollect Modules
from IHEWAcollect.base.exception import \
    IHEStringError, IHETypeError, IHEKeyError, IHEFileError

from IHEWAcollect.base.user import User
from IHEWAcollect.templates.gis import GIS
from IHEWAcollect.templates.dtime import Dtime

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


def test_user():
    path = os.path.join(__path)
    product = 'ALEXI'

    user = User(path, product, is_status=True)

    assert user.get_conf('file') == 'base.yml'
    # with pytest.raises(IHEKeyError, match=r".* IHEKeyError .*"):
    #     user.get_conf('test')


# def test_ALEXI():
#     # assert ALEXI.__version__ == '0.1'
#     path = os.path.join(__path_data, 'download')
#
#     timestep = 'daily'
#     ALEXI.DownloadData(
#         Dir=path,
#         Startdate='2007-02-01', Enddate='2007-03-01',
#         latlim=[50, 54], lonlim=[3, 7],
#         TimeStep=timestep,
#         Waitbar=1)
#     nfiles = len(os.listdir(os.path.join(
#         __path_data, 'download',
#         'Evaporation', 'ALEXI', 'Daily')))
#     print(nfiles)
#     assert nfiles > 0
