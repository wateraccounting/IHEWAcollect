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
    from .exception import \
        IHEStringError, IHETypeError, IHEKeyError, IHEFileError
except ImportError:
    from src.IHEWAcollect.base.exception \
        import IHEStringError, IHETypeError, IHEKeyError, IHEFileError

try:
    from .base import Base
except ImportError:
    from src.IHEWAcollect.base.base import Base


class GIS(Base):
    """This GIS class

    Description

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
        'path': '',
        'file': '',
        'data': {}
    }

    def __init__(self, workspace, is_status, **kwargs):
        """Class instantiation
        """
        Base.__init__(self, is_status)
        # super(GIS, self).__init__(is_status)

        vname, rtype, vdata = 'is_status', bool, is_status
        if self.check_input(vname, rtype, vdata):
            self.__status['is_print'] = vdata
        else:
            self.__status['code'] = 1

        vname, rtype, vdata = 'workspace', str, workspace
        if self.check_input(vname, rtype, vdata):
            self.__conf['path'] = vdata
        else:
            self.__status['code'] = 1

        if self.__status['code'] == 0:
            # self._conf()
            self.__status['message'] = ''

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

    def get_tif(self, file='', band=1):
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
            >>> data = gis.get_tif(file, 1)

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
        Data = np.ndarray

        if band == '':
            band = 1

        fp = gdal.Open(file)
        if fp is not None:
            try:
                Data = fp.GetRasterBand(band).ReadAsArray()
            except AttributeError:
                raise IHEKeyError('Band {b}'.format(b=band), file) from None
                # raise AttributeError('Band {band} not found.'.format(band=band))
        else:
            raise IHEFileError(file)from None
            # raise IOError('{} not found.'.format(file))

        return Data

    def save_tif(self, name='', data='', geo='', projection=''):
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

            >>> data = gis.get_tif(file, 1)
            >>> data
            array([[255, 255, 255, ...   0,   0,   0],
                   [255, 255, 255, ...   0,   0,   0],
                   [255, 255, 255, ...   0,   0,   0],
                   ...,
                   [  0,   0,   0, ...,   0,   0,   0],
                   [  0,   0,   0, ...,   0,   0,   0],
                   [  0,   0,   0, ...,   0,   0,   0]], dtype=uint8)

            >>> gis.save_tif(test, data, [0, 1, 0, 0, 1, 0], "WGS84")
            >>> data = gis.get_tif(test, 1)
            >>> data
            array([[255., 255., 255., ...   0.,   0.,   0.],
                   [255., 255., 255., ...   0.,   0.,   0.],
                   [255., 255., 255., ...   0.,   0.,   0.],
                   ...,
                   [  0.,   0.,   0., ...,   0.,   0.,   0.],
                   [  0.,   0.,   0., ...,   0.,   0.,   0.],
                   [  0.,   0.,   0., ...,   0.,   0.,   0.]], dtype=float32)
        """
        # save as a geotiff
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

        return

    def save_netcdf(self):
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
        '../', '../', '../'
    )
    gis = GIS(path, is_status=True)

    # Base attributes
    print('\ngis._Base__conf\n=====')
    # pprint(gis._Base__conf)

    # GIS attributes
    print('\ngis._GIS__conf:\n=====')
    print(gis._GIS__conf['data'].keys())
    # pprint(gis._GIS__conf)

    # GIS methods
    print('\ngis.Base.get_status()\n=====')
    pprint(gis.get_status())


if __name__ == "__main__":
    main()
