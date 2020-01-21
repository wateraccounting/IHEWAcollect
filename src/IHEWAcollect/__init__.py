# -*- coding: utf-8 -*-
"""
IHEWAcollect: IHE Water Accounting Collect Tools

`Restrictions`

The data and this python file may not be distributed to others without
permission of the WA+ team.

`Description`

This module contains scripts used to download Level 1 data (data directly from web).

+---------------------+-----------------------+---------------+
| Products            | Dates                 | Password      |
+=====================+=======================+===============+
| ALEXI (daily)       | 2005/01/01-2016/12/31 | WA+ FTP       |
+---------------------+-----------------------+---------------+
| ALEXI (monthly)     | 2005/01/01-2016/12/31 | WA+ FTP       |
+---------------------+-----------------------+---------------+
| ASCAT (daily)       | 2007/01/01-now        | VITO          |
+---------------------+-----------------------+---------------+
| CFSR (daily)        | 1979/01/01-now        |               |
+---------------------+-----------------------+---------------+
| CHIRPS (daily)      | 1981/01/01-now        |               |
+---------------------+-----------------------+---------------+
| CHIRPS (monthly)    | 1981/01/01-now        |               |
+---------------------+-----------------------+---------------+
| CMRSET (monthly)    | 2000/01/01-2012/12/31 | WA+ FTP       |
+---------------------+-----------------------+---------------+
| DEM                 |                       |               |
+---------------------+-----------------------+---------------+
| ECMWF               | 1979/01/01-now        | ECMWF_API     |
+---------------------+-----------------------+---------------+
| ETmonitor (monthly) | 2008/01/01-2013/12/31 | WA+ FTP       |
+---------------------+-----------------------+---------------+
| GLDAS               | 2000/01/01-now        | NASA          |
+---------------------+-----------------------+---------------+
| GLEAM (daily)       | 2007/01/01-2017/12/31 | GLEAM         |
+---------------------+-----------------------+---------------+
| GLEAM (monthly)     | 2007/01/01-2017/12/31 | GLEAM         |
+---------------------+-----------------------+---------------+
| HiHydroSoil         |                       | WA+ FTP       |
+---------------------+-----------------------+---------------+
| JRC                 |                       |               |
+---------------------+-----------------------+---------------+
| MCD43 (daily)       | 2000/02/24-now        | NASA          |
+---------------------+-----------------------+---------------+
| MOD10 (8-daily)     | 2000/02/18-now        | NASA          |
+---------------------+-----------------------+---------------+
| MOD11 (daily)       | 2000/02/24-now        | NASA          |
+---------------------+-----------------------+---------------+
| MOD11 (8-daily)     | 2000/02/18-now        | NASA          |
+---------------------+-----------------------+---------------+
| MOD12 (yearly)      | 2001/01/01-2013/12/31 | NASA          |
+---------------------+-----------------------+---------------+
| MOD13 (16-daily)    | 2000/02/18-now        | NASA          |
+---------------------+-----------------------+---------------+
| MOD15 (8-daily)     | 2000/02/18-now        | NASA          |
+---------------------+-----------------------+---------------+
| MOD16 (8-daily)     | 2000/01/01-2014/12/31 | NASA          |
+---------------------+-----------------------+---------------+
| MOD16 (monthly)     | 2000/01/01-2014/12/31 | NASA          |
+---------------------+-----------------------+---------------+
| MOD17 (8-daily GPP) | 2000/02/18-now        | NASA          |
+---------------------+-----------------------+---------------+
| MOD17 (yearly NPP)  | 2000/02/18-2015/12/31 | NASA          |
+---------------------+-----------------------+---------------+
| MOD9 (daily)        | 2000/02/24-now        | NASA          |
+---------------------+-----------------------+---------------+
| MSWEP (daily)       | 1979/01/01-now        | MSWEP         |
+---------------------+-----------------------+---------------+
| MSWEP (monthly)     | 1979/01/01-now        | MSWEP         |
+---------------------+-----------------------+---------------+
| MYD13 (16-daily)    | 2000/02/18-now        | NASA          |
+---------------------+-----------------------+---------------+
| RFE (daily)         | 2001/01/01-now        |               |
+---------------------+-----------------------+---------------+
| RFE (monthly)       | 2001/01/01-now        |               |
+---------------------+-----------------------+---------------+
| SEBS (monthly)      | 2000/03/01-2015/12/31 | WA+ guest FTP |
+---------------------+-----------------------+---------------+
| SSEBop (monthly)    | 2003/01/01-2014/10/31 | WA+ FTP       |
+---------------------+-----------------------+---------------+
| SoilGrids           |                       |               |
+---------------------+-----------------------+---------------+
| TRMM (daily)        | 1998/01/01-2018/06/29 | NASA          |
+---------------------+-----------------------+---------------+
| TRMM (monthly)      | 1998/01/01-2018/06/30 | NASA          |
+---------------------+-----------------------+---------------+
| TWC                 |                       | WA+ guest FTP |
+---------------------+-----------------------+---------------+

**Examples:**
::

    from watools import Collect
    help(Collect)
    dir(Collect)

.. note::

    Save user account and password, from your ``config.yml`` file.


.. seealso::

    - `Internet Protocols <https://www.restapitutorial.com/httpstatuscodes.html>`_
    - `datetime strftime code <http://strftime.org/>`_

.. todo::

    20190931, QPan, Collect module

    1. Create `config.yml` contains
        a. Portal name
        b. Portal url
        c. Portal data name, directory
        d. Portal data range, resolution
        e. Portal data file name template on ftp
        f. Portal data file name template on local
    2. cryptography `config.yml` file
    3. Add exception to check data meta information
    4. Estimate data size and tiff location to decided download or not
    5. Add unit test, and test datasets under "tests/data"
    6. read `__version__` from setup.py (git tag)
"""


from pkg_resources import get_distribution, DistributionNotFound

try:
    # Change here if project is renamed and does not equal the package name
    dist_name = 'WaterAccounting'
    __version__ = get_distribution(dist_name).version
except DistributionNotFound:
    __version__ = 'unknown'
finally:
    del get_distribution, DistributionNotFound

# TODO, 20200116, QPan, __init__, decide IHEWAcollect.download.Download() OR IHEWAcollect(args)
# import IHEWAcollect.download import Download

# import IHEWAcollect
# IHEWAcollect(args)