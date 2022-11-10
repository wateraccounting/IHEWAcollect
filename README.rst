.. -*- mode: rst -*-

|CoverAlls|_ |Travis|_ |ReadTheDocs|_ |DockerHub|_ |PyPI|_ |Zenodo|_

.. |CoverAlls| image:: https://coveralls.io/repos/github/wateraccounting/IHEWAcollect/badge.svg?branch=master
.. _CoverAlls: https://coveralls.io/github/wateraccounting/IHEWAcollect?branch=master

.. |Travis| image:: https://travis-ci.org/wateraccounting/IHEWAcollect.svg?branch=master
.. _Travis: https://travis-ci.org/wateraccounting/IHEWAcollect

.. |ReadTheDocs| image:: https://readthedocs.org/projects/ihewacollect/badge/?version=latest
.. _ReadTheDocs: https://ihewacollect.readthedocs.io/en/latest/

.. |DockerHub| image:: https://img.shields.io/docker/cloud/build/ihewa/ihewacollect
.. _DockerHub: https://hub.docker.com/r/ihewa/ihewacollect

.. |PyPI| image:: https://img.shields.io/pypi/v/IHEWAcollect
.. _PyPI: https://pypi.org/project/IHEWAcollect/

.. |Zenodo| image:: https://zenodo.org/badge/221895385.svg
.. _Zenodo: https://zenodo.org/badge/latestdoi/221895385


IHEWAcollect
============

IHE WaterAccounting Collect Tool. Tool to download open access remote sensing datasets for a geographical area and time period of interest.
Data is converted from original file format to .tiff format. 


Products
--------
List of products which can be downloaded through the IHEWAcollect package: 
https://ihewacollect.readthedocs.io/en/latest/products.html


Installation
-------
See installation notes on our wiki page: https://github.com/wateraccounting/IHEWAcollect/wiki/Installation

In order to have access to all products, accounts are needed from the following providers:
(`username, password` or `apitoken`)


+------------+-----------------------------------------------------------------------+
| Accounts   | Link                                                                  |
+============+=======================================================================+
| Copernicus | https://www.copernicus.eu/en                                          |
+------------+-----------------------------------------------------------------------+
| ECMWF      | https://www.ecmwf.int                                                 |
+------------+-----------------------------------------------------------------------+
| GLEAM      | http://www.gleam.eu                                                   |
+------------+-----------------------------------------------------------------------+
| NASA       | https://www.nasa.gov                                                  |
+------------+-----------------------------------------------------------------------+
| VITO       | https://www.vito-eodata.be/PDF/datapool                               |
+------------+-----------------------------------------------------------------------+
| WaPOR      | http://www.fao.org/in-action/remote-sensing-for-water-productivity/en |
+------------+-----------------------------------------------------------------------+

Usage
-------


Licence
-------
This work is licensed under a Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License
http://creativecommons.org/licenses/by-nc-sa/4.0/

.. image:: https://i.creativecommons.org/l/by-nc-sa/4.0/88x31.png
   :width: 150
   :alt: "Creative Commons License"
