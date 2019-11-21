# -*- coding: utf-8 -*-
"""
    Setup file for IHEWAcollect.
    Use setup.cfg to configure your project.

    This file was generated with PyScaffold 3.2.2.
    PyScaffold helps you to put up the scaffold of your new Python project.
    Learn more under: https://pyscaffold.org/
    Learn more under: https://pyscaffold.org/en/latest/features.html

    To use this feature you need to tag with the format vMAJOR.MIN0OR[.PATCH] ,
    e.g. 0.0.1 or 0.1.
"""
import sys

from pkg_resources import VersionConflict, require
from setuptools import setup

try:
    require('setuptools>=38.3')
except VersionConflict:
    print("Error: version of setuptools is too old (<38.3)!")
    sys.exit(1)

if __name__ == "__main__":
    setup(use_pyscaffold=True)
