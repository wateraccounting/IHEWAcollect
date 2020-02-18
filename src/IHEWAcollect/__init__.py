# -*- coding: utf-8 -*-
"""
IHEWAcollect: IHE Water Accounting Collect Tools
"""


from pkg_resources import get_distribution, DistributionNotFound

try:
    # Change here if project is renamed and does not equal the package name
    dist_name = 'IHEWAcollect'
    __version__ = get_distribution(dist_name).version
except DistributionNotFound:
    __version__ = 'unknown'
finally:
    del get_distribution, DistributionNotFound

try:
    from .download import Download
except ImportError:
    from IHEWAcollect.download import Download
__all__ = ['Download']

# TODO, 20190931, QPan, Collect module
#  1. Create `config.yml` contains
#      a. Portal name
#      b. Portal url
#      c. Portal data name, directory
#      d. Portal data range, resolution
#      e. Portal data file name template on ftp
#      f. Portal data file name template on local
#  2. cryptography `config.yml` file
#  3. Add exception to check data meta information
#  4. Estimate data size and tiff location to decided download or not
#  5. Add unit test, and test datasets under "tests/data"
#  6. read `__version__` from setup.py (git tag)
#
# TODO, 20200128, QPan, __init__
#  Check, envorinment, dependeny, library
