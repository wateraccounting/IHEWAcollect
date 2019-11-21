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
    from .base import Base
except ImportError:
    from src.IHEWAcollect.base.base import Base


class GIS(Base):
    """This Base class

    Description

    Args:
      workspace (str): Directory to accounts.yml.
      account (str): Account name of data product.
      is_status (bool): Is to print status message.
      kwargs (dict): Other arguments.
    """
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

        self.stmsg = {
            0: 'S: WA.GIS "{f}" status {c}: {m}',
            1: 'E: WA.GIS "{f}" status {c}: {m}',
            2: 'W: WA.GIS "{f}" status {c}: {m}',
        }
        self.stcode = 0
        self.status = 'GIS status.'

        if isinstance(workspace, str):
            if workspace != '':
                self.__conf['path'] = workspace
            else:
                self.__conf['path'] = os.path.join(
                    self._Base__conf['path'], '../', '../', '../'
                )
            if self.is_status:
                print('"{k}": "{v}"'
                      .format(k='workspace',
                              v=self.__conf['path']))
        else:
            raise TypeError('"{k}" requires string, received "{t}"'
                            .format(k='workspace',
                                    t=type(workspace)))

        if self.stcode == 0:
            # self._conf()
            message = ''

        self._status(
            inspect.currentframe().f_code.co_name,
            prt=self.is_status,
            ext=message)

    def _status(self, fun, prt=False, ext=''):
        """Set status

        Args:
          fun (str): Function name.
          prt (bool): Is to print on screen?
          ext (str): Extra message.
        """
        self.status = self.set_status(self.stcode, fun, prt, ext)

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

        f = gdal.Open(file)
        if f is not None:
            try:
                Data = f.GetRasterBand(band).ReadAsArray()
            except AttributeError:
                raise AttributeError('Band {band} not found.'.format(band=band))
        else:
            raise IOError('{} not found.'.format(file))

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
        dst_ds = driver.Create(name, int(data.shape[1]), int(data.shape[0]), 1,
                               gdal.GDT_Float32, ['COMPRESS=LZW'])
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
    gis = GIS('', is_status=True)

    # Base attributes
    print('\ngis._Base__conf\n=====')
    pprint(gis._Base__conf)

    # GIS attributes
    print('\ngis._GIS__conf:\n=====')
    pprint(gis._GIS__conf)

    # GIS methods
    print('\ngis.Base.get_status()\n=====')
    pprint(gis.get_status())


if __name__ == "__main__":
    main()
