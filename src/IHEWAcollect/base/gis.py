# -*- coding: utf-8 -*-
"""
**GIS**

`Restrictions`

The data and this python file may not be distributed to others without
permission of the WA+ team.

`Description`

Before use this module, set account information
in the ``WaterAccounting/accounts.yml`` file.

**Examples:**
::

    import os
    from IHEWAcollect.base.gis import GIS
    gis = GIS(os.getcwd(), is_status=True)

.. note::

    1. Create ``accounts.yml`` under root folder of the project,
       based on the ``config-example.yml``.
    #. Run ``Collect.credential.encrypt_cfg(path, file, password)``
       to generate ``accounts.yml-encrypted`` file.
    #. Save key to ``credential.yml``.

"""
import os
# import sys
import inspect
# import shutil
# import yaml
# from datetime import datetime

import numpy as np

try:
    from osgeo import gdal, osr, gdalconst
except ImportError:
    import gdal
    import osr
    import gdalconst

try:
    from .base.exception import IHEClassInitError,\
        IHEStringError, IHETypeError, IHEKeyError, IHEFileError
except ImportError:
    from src.IHEWAcollect.base.exception import IHEClassInitError,\
        IHEStringError, IHETypeError, IHEKeyError, IHEFileError


class GIS(object):
    """This GIS class

    GIS process. Standard CRS is "EPSG:4326 - WGS 84 - Geographic".

    Args:
      workspace (str): Directory to accounts.yml.
      is_status (bool): Is to print status message.
      kwargs (dict): Other arguments.
    """
    status = 'Global status.'

    __status = {
        'messages': {
            0: 'S: WA.GIS      {f:>20} : status {c}, {m}',
            1: 'E: WA.GIS      {f:>20} : status {c}: {m}',
            2: 'W: WA.GIS      {f:>20} : status {c}: {m}',
        },
        'code': 0,
        'message': '',
        'is_print': True
    }

    __conf = {
        'file': '',
        'path': '',
        'data': {}
    }

    def __init__(self, workspace, is_status, **kwargs):
        """Class instantiation
        """
        # # super(GIS, self).__init__(is_status)
        # Base.__init__(self, is_status)

        # Class self.__status['is_print']
        self.__status['is_print'] = is_status

        # Class self.__conf['path']
        self.__conf['path'] = workspace

    def set_status(self, fun='', prt=False, ext=''):
        """Set status

        Args:
          fun (str): Function name.
          prt (bool): Is to print on screen?
          ext (str): Extra message.
        """
        self.status = self._status(self.__status['messages'],
                                   self.__status['code'],
                                   fun, prt, ext)

    def check_continent(self, lat, lon, conf_lat, conf_lon):
        """Check area located in continent or continents, based on HydroSHEDS

        HydroSHEDS:

          - af: Africa,          lat [s:-35.0, n: 38.0], lon [w: -19.0, e:  55.0].
          - as: Asia,            lat [s:-12.0, n: 61.0], lon [w:  57.0, e: 180.0].
          - au: Australia,       lat [s:-56.0, n:-10.0], lon [w: 112.0, e: 180.0].
          - ca: Central America, lat [s:  5.0, n: 39.0], lon [w:-119.0, e: -60.0].
          - eu: Europe,          lat [s: 12.0, n: 62.0], lon [w: -14.0, e:  70.0].
          - na: North America,   lat [s: 24.0, n: 60.0], lon [w:-138.0, e: -52.0].
          - sa: South America,   lat [s:-56.0, n: 15.0], lon [w: -93.0, e: -32.0].
        """
        pass

    def check_latlon_limit(self, lat, lon, conf_lat, conf_lon):
        """
        """
        latlim, lonlim = [], []

        if lat[0] < conf_lat.s or lat[1] > conf_lat.n:
            print(
                'Latitude above 70N or below 60S is not possible. Value set to maximum')
            latlim[0] = np.max(lat[0], conf_lat.s)
            latlim[1] = np.min(lat[1], conf_lat.n)

        if lon[0] < conf_lon.w or lon[1] > conf_lon.e:
            print(
                'Longitude must be between 180E and 180W. Now value is set to maximum')
            lonlim[0] = np.max(lon[0], conf_lon.w)
            lonlim[1] = np.min(lon[1], conf_lon.e)

        return latlim, lonlim

    def get_latlon_index(self, lat, lon, conf_dem):
        latid, lonid = np.ndarray, np.ndarray

        # # Define IDs
        # latid = 3000 - np.int16(
        #     np.array(
        #         [np.ceil((latlim[1] + 60) * 20), np.floor((latlim[0] + 60) * 20)]))
        # lonid = np.int16(
        #     np.array(
        #         [np.floor((lonlim[0]) * 20), np.ceil((lonlim[1]) * 20)]) + 3600)

        return latid, lonid

    def load_file(self, file='', band=1):
        """Get tif band data

        This function get tif band as numpy.ndarray.

        Args:
          file (str): 'C:/file/to/path/file.tif' or a gdal file (gdal.Open(file))
            string that defines the input tif file or gdal file.
          band (int): Defines the band of the tif that must be opened.

        Returns:
          :obj:`numpy.ndarray`: Band data.

        :Example:

            >>> import os
            >>> from IHEWAcollect.base.gis import GIS
            >>> gis = GIS(os.getcwd(), is_status=False)
            >>> path = os.path.join(os.getcwd(), 'tests', 'data', 'BigTIFF')
            >>> file = os.path.join(path, 'Classic.tif')
            >>> data = gis.load_file(file, 1)

            >>> type(data)
            <class 'numpy.ndarray'>

            >>> data.shape
            (64, 64)

            >>> data
            array([[255, 255, 255, ...   0,   0,   0],
                   [255, 255, 255, ...   0,   0,   0],
                   [255, 255, 255, ...   0,   0,   0],
                   ...,
                   [  0,   0,   0, ...,   0,   0,   0],
                   [  0,   0,   0, ...,   0,   0,   0],
                   [  0,   0,   0, ...,   0,   0,   0]], dtype=uint8)
        """
        data = np.ndarray

        if band == '':
            band = 1

        fp = gdal.Open(file)
        if fp is not None:
            try:
                data = fp.GetRasterBand(band).ReadAsArray()
            except AttributeError:
                raise IHEKeyError('Band {b}'.format(b=band), file) from None
                # raise AttributeError('Band {band} not found.'.format(band=band))
        else:
            raise IHEFileError(file)from None
            # raise IOError('{} not found.'.format(file))

        return data

    def merge_data(self, data):
        pass

    def clip_data(self, data):
        pass

    def save_GTiff(self, name='', data='', geo='', projection=''):
        """Save as tif

        This function save the array as a geotiff.

        Args:
          name (str): Directory name.
          data (:obj:`numpy.ndarray`): Dataset of the geotiff.
          geo (list): Geospatial dataset, [minimum lon, pixelsize, rotation,
            maximum lat, rotation, pixelsize].
          projection (int): EPSG code.

        :Example:

            >>> from IHEWAcollect.base.gis import GIS
            >>> gis = GIS(os.getcwd(), is_status=False)
            >>> path = os.path.join(os.getcwd(), 'tests', 'data', 'BigTIFF')
            >>> file = os.path.join(path, 'Classic.tif')
            >>> test = os.path.join(path, 'test.tif')

            >>> data = gis.load_file(file, 1)
            >>> data
            array([[255, 255, 255, ...   0,   0,   0],
                   [255, 255, 255, ...   0,   0,   0],
                   [255, 255, 255, ...   0,   0,   0],
                   ...,
                   [  0,   0,   0, ...,   0,   0,   0],
                   [  0,   0,   0, ...,   0,   0,   0],
                   [  0,   0,   0, ...,   0,   0,   0]], dtype=uint8)

            >>> gis.save_GTiff(test, data, [0, 1, 0, 0, 1, 0], "WGS84")
            >>> data = gis.load_file(test, 1)
            >>> data
            array([[255., 255., 255., ...   0.,   0.,   0.],
                   [255., 255., 255., ...   0.,   0.,   0.],
                   [255., 255., 255., ...   0.,   0.,   0.],
                   ...,
                   [  0.,   0.,   0., ...,   0.,   0.,   0.],
                   [  0.,   0.,   0., ...,   0.,   0.,   0.],
                   [  0.,   0.,   0., ...,   0.,   0.,   0.]], dtype=float32)
        """
        driver = gdal.GetDriverByName("GTiff")
        dst_ds = driver.Create(name,
                               int(data.shape[1]), int(data.shape[0]),
                               1,
                               gdal.GDT_Float32,
                               ['COMPRESS=LZW'])
        srse = osr.SpatialReference()
        if projection == '':
            srse.SetWellKnownGeogCS("WGS84")

        else:
            try:
                if not srse.SetWellKnownGeogCS(projection) == 6:
                    srse.SetWellKnownGeogCS(projection)
                else:
                    try:
                        srse.ImportFromEPSG(int(projection))
                    except BaseException as err:
                        print(err)
                    else:
                        srse.ImportFromWkt(projection)
            except BaseException:
                try:
                    srse.ImportFromEPSG(int(projection))
                except BaseException as err:
                    print(err)
                else:
                    srse.ImportFromWkt(projection)

        dst_ds.SetProjection(srse.ExportToWkt())
        dst_ds.SetGeoTransform(geo)
        dst_ds.GetRasterBand(1).SetNoDataValue(-9999)
        dst_ds.GetRasterBand(1).WriteArray(data)
        dst_ds = None

    def save_NetCDF(self):
        pass


def main():
    from pprint import pprint

    # @classmethod

    # GIS __init__
    print('\nGIS\n=====')
    path = os.path.join(
        os.getcwd(),
        os.path.dirname(
            inspect.getfile(
                inspect.currentframe())),
        '../', '../', '../', 'tests'
    )
    gis = GIS(path, is_status=True)

    # GIS attributes
    print('\ngis._GIS__conf:\n=====')
    pprint(gis._GIS__conf)
    # print(gis._GIS__conf['data'].keys())

    # # GIS methods
    # print('\ngis.Base.get_status()\n=====')
    # pprint(gis.get_status())


if __name__ == "__main__":
    main()
