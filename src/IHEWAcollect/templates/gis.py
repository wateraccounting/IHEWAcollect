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
    gis = GIS(os.getcwd(), is_print=True)

.. note::

    1. Create ``accounts.yml`` under root folder of the project,
       based on the ``config-example.yml``.
    #. Run ``Collect.credential.encrypt_cfg(path, file, password)``
       to generate ``accounts.yml-encrypted`` file.
    #. Save key to ``credential.yml``.

"""
import os
import sys
import inspect
import subprocess

import numpy as np
# import pandas as pd

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
    from IHEWAcollect.base.exception import IHEClassInitError,\
        IHEStringError, IHETypeError, IHEKeyError, IHEFileError


class GIS(object):
    """This GIS class

    GIS process. Standard CRS is "EPSG:4326 - WGS 84 - Geographic".

    HydroSHEDS:

      - af: Africa,          lat [s:-35.0, n: 38.0], lon [w: -19.0, e:  55.0].
      - as: Asia,            lat [s:-12.0, n: 61.0], lon [w:  57.0, e: 180.0].
      - au: Australia,       lat [s:-56.0, n:-10.0], lon [w: 112.0, e: 180.0].
      - ca: Central America, lat [s:  5.0, n: 39.0], lon [w:-119.0, e: -60.0].
      - eu: Europe,          lat [s: 12.0, n: 62.0], lon [w: -14.0, e:  70.0].
      - na: North America,   lat [s: 24.0, n: 60.0], lon [w:-138.0, e: -52.0].
      - sa: South America,   lat [s:-56.0, n: 15.0], lon [w: -93.0, e: -32.0].

    Args:
      workspace (str): Directory to accounts.yml.
      is_print (bool): Is to print status message.
      kwargs (dict): Other arguments.
    """
    status = 'Global status.'

    __status = {}
    __conf = {}

    conf = {
        'file': {
            'i': '',
            'o': ''
        },
        'latlim': {
            's': 0.0,
            'n': 0.0,
            'r': 0.0
        },
        'lonlim': {
            'w': 0.0,
            'e': 0.0,
            'r': 0.0
        },
        'dem': {
            'w': 0,
            'h': 0
        },
        'latlon': {
            'w': 0.0,
            'n': 0.0,
            'e': 0.0,
            's': 0.0
        },
        # 'dtype': {},
        'data': {}
    }

    def __init__(self, __status, __conf, **kwargs):
        """Class instantiation
        """
        # print('GIS.__init__')
        self.__status = __status
        self.__status = {
            'messages': {
                0: 'S: WA.GIS      {f:>20} : status {c}, {m}',
                1: 'E: WA.GIS      {f:>20} : status {c}: {m}',
                2: 'W: WA.GIS      {f:>20} : status {c}: {m}',
            }
        }
        self.__conf = __conf

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

    def get_latlon_lim(self, arg_bbox):
        prod_lat = self.product['data']['lat']
        prod_lon = self.product['data']['lon']
        prod_dem = self.product['data']['dem']

        # from osgeo import osr
        #
        # src = osr.SpatialReference()
        # tgt = osr.SpatialReference()
        # src.ImportFromEPSG(4326)
        # tgt.ImportFromEPSG(int(data['crs']))
        #
        # transform = osr.CoordinateTransformation(src, tgt)
        # coords = transform.TransformPoint(-122, 46)
        # x, y = coords[0:2]

        arg_lat = [
            np.max(
                [
                    arg_bbox['s'],
                    prod_lat['s']
                ]
            ),
            np.min(
                [
                    arg_bbox['n'],
                    prod_lat['n']
                ]
            )
        ]

        arg_lon = [
            np.max(
                [
                    arg_bbox['w'],
                    prod_lon['w']
                ]
            ),
            np.min(
                [
                    arg_bbox['e'],
                    prod_lon['e']
                ]
            )
        ]
        return arg_lat, arg_lon

    def get_latlon_index(self, arg_lat, arg_lon) -> tuple:
        prod_lat = self.product['data']['lat']
        prod_lon = self.product['data']['lon']
        prod_dem = self.product['data']['dem']

        y_id = np.int16(
            np.array([
                3000 - np.ceil((arg_lat[1] + 60) * 20),
                3000 - np.floor((arg_lat[0] + 60) * 20)
            ]))

        x_id = np.int16(
            np.array([
                np.floor((arg_lon[0]) * 20) + 3600,
                np.ceil((arg_lon[1]) * 20) + 3600
            ]))
        return y_id, x_id

    def check_continent(self, arg_lat, arg_lon) -> list:
        """Check area located in continent or continents, based on HydroSHEDS
        """
        continent_list = {
            'af': {
                'w': -19.0,
                'n': 38.0,
                'e': 55.0,
                's': -35.0
            },
            'as': {
                'w': 57.0,
                'n': 61.0,
                'e': 180.0,
                's': -12.0
            },
            'au': {
                'w': 112.0,
                'n': -10.0,
                'e': 180.0,
                's': -56.0
            },
            'ca': {
                'w': -119.0,
                'n': 39.0,
                'e': -60.0,
                's': 5.0
            },
            'eu': {
                'w': -14.0,
                'n': 62.0,
                'e': 70.0,
                's': 12.0
            },
            'na': {
                'w': -138.0,
                'n': 60.0,
                'e': -52.0,
                's': 24.0
            },
            'sa': {
                'w': -93.0,
                'n': 15.0,
                'e': -32.0,
                's': -56.0
            },
        }
        continents = []
        return continents

    def load_file(self, file, band=1) -> np.ndarray:
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
            >>> from IHEWAcollect.templates.gis import GIS
            >>> gis = GIS(os.getcwd(), is_print=False)
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

        ds = gdal.Open(file)
        if ds is None:
            raise IHEFileError(file) from None
        else:
            if band is None:
                band = 1
            # data = fp.GetRasterBand(band).ReadAsArray()

            if ds.RasterCount > 0:
                try:
                    ds_band = ds.GetRasterBand(band)
                    if ds_band is None:
                        pass
                    else:
                        ds_band_ndv = ds_band.GetNoDataValue()
                        ds_band_scale = ds_band.GetScale()
                        ds_band_unit = ds_band.GetUnitType()

                        data = ds_band.ReadAsArray()

                        # Check data type
                        if isinstance(data, np.ma.MaskedArray):
                            data = data.filled()
                        else:
                            data = np.asarray(data)

                        # convert to float
                        data = data.astype(np.float32)

                        if np.logical_or(isinstance(ds_band_ndv, str),
                                         isinstance(ds_band_scale, str)):
                            ds_band_ndv = float(ds_band_ndv)
                            ds_band_scale = float(ds_band_scale)

                        # Convert units, set NVD
                        if ds_band_ndv is not None:
                            data[data == ds_band_ndv] = np.nan
                        if ds_band_scale is not None:
                            data = data * ds_band_scale

                except BaseException as err:
                    raise IHEKeyError('Band {b}'.format(b=band), file) from None
            else:
                raise IHEFileError(file) from None

        ds = None
        return data

    def merge_map(self, data) -> np.ndarray:
        rtn_data = np.zeros([1, 1])
        return rtn_data

    def clip_map(self, data) -> np.ndarray:
        rtn_data = np.zeros([1, 1])
        return rtn_data

    def saveas_GTiff(self, name, data, geo, projection, ndv):
        """Save as tif

        This function save the array as a geotiff.

        Args:
          name (str): Directory name.
          data (:obj:`numpy.ndarray`): Dataset of the geotiff.
          geo (list): Geospatial dataset, [minimum lon, pixelsize, rotation,
            maximum lat, rotation, pixelsize].
          projection (int): EPSG code.

        :Example:

            >>> from IHEWAcollect.templates.gis import GIS
            >>> gis = GIS(os.getcwd(), is_print=False)
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

            >>> gis.saveas_GTiff(test, data, [0, 1, 0, 0, 1, 0], "WGS84", -9999)
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
        status = -1

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
        dst_ds.GetRasterBand(1).SetNoDataValue(ndv)
        dst_ds.GetRasterBand(1).WriteArray(data)
        dst_ds = None
        return status

    def saveas_NetCDF(self) -> int:
        status = -1
        return status

    def reproject_MODIS(self, file_i, file_o, epsg_str) -> int:
        """Reproject the map

        The input projection must be the MODIS projection.
        The output projection can be defined by the user.
        """
        status = -1

        # Get environmental variable
        # WA_env_paths = os.environ["GDAL_DRIVER"].split(';')
        # GDAL_env_path = WA_env_paths[0]
        # GDALWARP_PATH = os.path.join(GDAL_env_path, 'gdalwarp.exe')

        exe_str = 'gdalwarp.exe'

        cmd_str = '{para1} {para2} {para3} {para4} {para5} {fi} {fo}'.format(
            para1='-overwrite',
            para2='-s_srs',
            para3='"{0} {1} {2} {3} {4} {5} {6}"'.format(
                '+proj=sinu',
                '+lon_0=0',
                '+x_0=0 +y_0=0',
                '+a=6371007.181',
                '+b=6371007.181',
                '+units=m',
                '+no_defs'
            ),
            para4='-t_srs EPSG:%s' % epsg_str,
            para5='-of GTiff',
            fi=file_i,
            fo=file_o
        )
        # -r {nearest}

        status = self.exe_cmd(exe_str, cmd_str)
        return status

    def exe_cmd(self, exe_name, cmd_str) -> int:
        """
        This function runs the argument in the command window without showing cmd window

        Keyword Arguments:
        argument -- string, name of the adf file
        """
        # print('\n{}'.format(argument))
        status = -1

        if os.name == 'posix':
            exe_str = exe_name.replace(".exe", "")
        else:
            exe_str = exe_name
        cmd = '{exe} {cmd}'.format(exe=exe_str, cmd=cmd_str)

        if os.name == 'posix':
            status = os.system(cmd)

        else:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

            process = subprocess.Popen(cmd,
                                       startupinfo=startupinfo,
                                       stderr=subprocess.PIPE,
                                       stdout=subprocess.PIPE)
            status = process.wait()

        if status != 0:
            raise RuntimeError(cmd)
        return status


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
    gis = GIS(path, is_print=True)

    # GIS attributes
    print('\ngis._GIS__conf:\n=====')
    pprint(gis._GIS__conf)
    # print(gis._GIS__conf['data'].keys())

    # # GIS methods
    # print('\ngis.Base.get_status()\n=====')
    # pprint(gis.get_status())


if __name__ == "__main__":
    main()
