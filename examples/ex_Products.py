# -*- coding: utf-8 -*-
import inspect
import os

import IHEWAcollect
import yaml


def main(path, test_args):
    # from pprint import pprint

    # Download __init__
    for key, value in test_args.items():
        print('\n{:>4s}'
              '{:>20s}{:>6s}{:>20s}{:>20s}{:>20s}\n'
              '{:->90s}'.format(key,
                                value['product'],
                                value['version'],
                                value['parameter'],
                                value['resolution'],
                                value['variable'],
                                '-'))

        IHEWAcollect.Download(workspace=path,
                              product=value['product'],
                              version=value['version'],
                              parameter=value['parameter'],
                              resolution=value['resolution'],
                              variable=value['variable'],
                              bbox=value['bbox'],
                              period=value['period'],
                              nodata=value['nodata'],
                              is_status=False)


def dump_to_yaml(path, test_args):
    fp = open(os.path.join(path, 'config.yml'), 'w+')
    yaml.dump(test_args, fp,
              default_flow_style=False, sort_keys=False,
              allow_unicode=True)


if __name__ == "__main__":
    path = os.path.join(
        os.getcwd(),
        os.path.dirname(
            inspect.getfile(
                inspect.currentframe()))
    )

    test_args = {
        '1a': {
            'product': 'ALEXI',
            'version': 'v1',
            'parameter': 'evapotranspiration',
            'resolution': 'daily',
            'variable': 'ETA',
            'bbox': {
                'w': -19.0,
                'n': 38.0,
                'e': 55.0,
                's': -35.0
            },
            'period': {
                's': '2005-01-01',
                'e': '2005-01-02'
            },
            'nodata': -9999
        },
        '1b': {
            'product': 'ALEXI',
            'version': 'v1',
            'parameter': 'evapotranspiration',
            'resolution': 'weekly',
            'variable': 'ETA',
            'bbox': {
                'w': -19.0,
                'n': 38.0,
                'e': 55.0,
                's': -35.0
            },
            'period': {
                's': '2005-01-01',
                'e': '2005-01-15'
            },
            'nodata': -9999
        },
        '2a': {
            'product': 'ASCAT',
            'version': 'v3.1.1',
            'parameter': 'soil_water_index',
            'resolution': 'daily',
            'variable': 'SWI_010',
            'bbox': {
                'w': -19.0,
                'n': 38.0,
                'e': 55.0,
                's': -35.0
            },
            'period': {
                's': '2007-01-01',
                'e': '2007-01-02'
            },
            'nodata': -9999
        },
        # TODO, 20200120-END, QPan, ex_CFSR_GRIB, Docker
        #  dec_jpeg2000
        # '3a': {
        #     # Caution:
        #     # dec_jpeg2000: Unable to open JPEG2000 image within GRIB file.
        #     # Docker, pass
        #
        #     'product': 'CFSR',
        #     'version': 'v1',
        #     'parameter': 'radiation',
        #     'resolution': 'daily',
        #     'variable': 'dlwsfc',
        #     'bbox': {
        #         'w': -19.0,
        #         'n': 38.0,
        #         'e': 55.0,
        #         's': -35.0
        #     },
        #     'period': {
        #         's': '2007-01-01',
        #         'e': '2007-01-02'
        #     },
        #     'nodata': -9999
        # },
        '4a': {
            'product': 'CHIRPS',
            'version': 'v2.0',
            'parameter': 'precipitation',
            'resolution': 'daily',
            'variable': 'PCP',
            'bbox': {
                'w': -19.0,
                'n': 38.0,
                'e': 55.0,
                's': -35.0
            },
            'period': {
                's': '2007-01-01',
                'e': '2007-01-02'
            },
            'nodata': -9999
        },
        '4b': {
            'product': 'CHIRPS',
            'version': 'v2.0',
            'parameter': 'precipitation',
            'resolution': 'monthly',
            'variable': 'PCP',
            'bbox': {
                'w': -19.0,
                'n': 38.0,
                'e': 55.0,
                's': -35.0
            },
            'period': {
                's': '2007-01-01',
                'e': '2007-01-02'
            },
            'nodata': -9999
        },
        '5a': {
            'product': 'CMRSET',
            'version': 'v1',
            'parameter': 'evapotranspiration',
            'resolution': 'monthly',
            'variable': 'ETA',
            'bbox': {
                'w': -19.0,
                'n': 38.0,
                'e': 55.0,
                's': -35.0
            },
            'period': {
                's': '2007-01-01',
                'e': '2007-01-31'
            },
            'nodata': -9999
        },
        # TODO, 20200120, QPan, DEM
        #  rewrite, and re-design base.yml
        '6a': {
            'product': 'DEM',
            'version': 'v1',
            'parameter': 'DEM',
            'resolution': '30s',
            'variable': 'af',
            'bbox': {
                'w': -19.0,
                'n': 38.0,
                'e': 55.0,
                's': -35.0
            },
            'period': {
                's': None,
                'e': None
            },
            'nodata': -9999
        },
        '6b': {
            'product': 'DEM',
            'version': 'v1',
            'parameter': 'DIR',
            'resolution': '30s',
            'variable': 'af',
            'bbox': {
                'w': -19.0,
                'n': 38.0,
                'e': 55.0,
                's': -35.0
            },
            'period': {
                's': None,
                'e': None
            },
            'nodata': -9999
        },
        # TODO, 20200120, QPan, ECMWF
        # '7a': {
        #     'product': 'ECMWF',
        # },
        # TODO, 20200120-END, QPan, ex_ETmonitor_BigTIFF, Docker
        #  Why gdal_translate.exe use less RAM?
        # '8a': {
        #     'product': 'ETmonitor',
        #     'version': 'v1',
        #     'parameter': 'evapotranspiration',
        #     'resolution': 'monthly',
        #     'variable': 'ETA',
        #     # variable': 'ETP',
        #     'bbox': {
        #         'w': -19.0,
        #         'n': 38.0,
        #         'e': 55.0,
        #         's': -35.0
        #     },
        #     'period': {
        #         's': '2008-01-01',
        #         'e': '2008-01-31'
        #     },
        #     'nodata': -9999
        # },
        # TODO, 20200129-END, QPan, FEWS (SEBS)
        #  multiplier: uint16 to float32, 0.01
        '9a': {
            'product': 'FEWS',
            'version': 'v4',
            'parameter': 'evapotranspiration',
            'resolution': 'daily',
            'variable': 'ETP',
            'bbox': {
                'w': -19.0,
                'n': 38.0,
                'e': 55.0,
                's': -35.0
            },
            'period': {
                's': '2008-01-01',
                'e': '2008-01-02'
            },
            'nodata': -9999
        },
        '10a': {
            'product': 'GLDAS',
            'version': 'v2.1',
            'parameter': 'evapotranspiration',
            'resolution': 'three_hourly',
            'variable': 'ETA',
            'bbox': {
                'w': -19.0,
                'n': 38.0,
                'e': 55.0,
                's': -35.0
            },
            'period': {
                's': '2008-01-01',
                'e': '2008-01-02'
            },
            'nodata': -9999
        },
        '10b': {
            'product': 'GLDAS',
            'version': 'v2.1',
            'parameter': 'evapotranspiration',
            'resolution': 'monthly',
            'variable': 'ETA',
            'bbox': {
                'w': -19.0,
                'n': 38.0,
                'e': 55.0,
                's': -35.0
            },
            'period': {
                's': '2008-01-01',
                'e': '2008-01-02'
            },
            'nodata': -9999
        },
        '11a': {
            'product': 'GLEAM',
            'version': 'v3.3a',
            'parameter': 'evapotranspiration',
            'resolution': 'daily',
            'variable': 'ETA',
            'bbox': {
                'w': -19.0,
                'n': 38.0,
                'e': 55.0,
                's': -35.0
            },
            'period': {
                's': '2008-01-01',
                'e': '2008-01-02'
            },
            'nodata': -9999
        },
        # TODO, 20200128-END, QPan, GLEAM
        #  date_id = (total month from time['s'])
        '11b': {
            'product': 'GLEAM',
            'version': 'v3.3a',
            'parameter': 'evapotranspiration',
            'resolution': 'monthly',
            'variable': 'ETA',
            'bbox': {
                'w': -180.0,
                'n': 90.0,
                'e': 180.0,
                's': -90.0
            },
            'period': {
                's': '2008-01-01',
                'e': '2008-01-02'
            },
            'nodata': -9999
        },
        '11c': {
            'product': 'GLEAM',
            'version': 'v3.3b',
            'parameter': 'evapotranspiration',
            'resolution': 'daily',
            'variable': 'ETA',
            'bbox': {
                'w': -19.0,
                'n': 38.0,
                'e': 55.0,
                's': -35.0
            },
            'period': {
                's': '2008-01-01',
                'e': '2008-01-02'
            },
            'nodata': -9999
        },
        '11d': {
            'product': 'GLEAM',
            'version': 'v3.3b',
            'parameter': 'evapotranspiration',
            'resolution': 'monthly',
            'variable': 'ETA',
            'bbox': {
                'w': -180.0,
                'n': 90.0,
                'e': 180.0,
                's': -90.0
            },
            'period': {
                's': '2008-01-01',
                'e': '2008-01-02'
            },
            'nodata': -9999
        },
        '12a': {
            'product': 'GPM',
            'version': 'v6',
            'parameter': 'precipitation',
            'resolution': 'daily',
            'variable': 'PCP',
            'bbox': {
                'w': -19.0,
                'n': 38.0,
                'e': 55.0,
                's': -35.0
            },
            'period': {
                's': '2008-01-01',
                'e': '2008-01-02'
            },
            'nodata': -9999
        },
        # TODO, 20200120-END, QPan, GPM
        #  product['data']['ftype']['r'].split('.')
        '12b': {
            'product': 'GPM',
            'version': 'v6',
            'parameter': 'precipitation',
            'resolution': 'monthly',
            'variable': 'PCP',
            'bbox': {
                'w': -180.0,
                'n': 90.0,
                'e': 180.0,
                's': -90.0
            },
            'period': {
                's': '2008-01-01',
                'e': '2008-01-02'
            },
            'nodata': -9999
        },
        '13a': {
            'product': 'HiHydroSoil',
            'version': 'v1',
            'parameter': 'soil',
            'resolution': '30s',
            'variable': 'wcsat_topsoil',
            'bbox': {
                'w': -19.0,
                'n': 38.0,
                'e': 55.0,
                's': -35.0
            },
            'period': {
                's': None,
                'e': None
            },
            'nodata': -9999
        },
        # TODO, 20200130-END, QPan, JRC
        #  Tiles, sn_gring_10deg.csv, memory usage
        '14a': {
            'product': 'JRC',
            'version': 'v1',
            'parameter': 'water',
            'resolution': '1s',
            'variable': 'occurrence',
            'bbox': {
                'w': -5.0,
                'n': 30.0,
                'e': 5.0,
                's': 25.0
            },
            'period': {
                's': None,
                'e': None
            },
            'nodata': -9999
        },
        '15a': {
            'product': 'MCD12Q1',
            'version': 'v6',
            'parameter': 'land',
            'resolution': 'yearly',
            'variable': 'LC',
            'bbox': {
                'w': -5.0,
                'n': 30.0,
                'e': 5.0,
                's': 25.0
            },
            'period': {
                's': '2008-01-01',
                'e': '2008-12-31'
            },
            'nodata': -9999
        },
        '15b': {
            'product': 'MCD12Q1',
            'version': 'v6',
            'parameter': 'land',
            'resolution': 'yearly',
            'variable': 'LU',
            'bbox': {
                'w': -5.0,
                'n': 30.0,
                'e': 5.0,
                's': 25.0
            },
            'period': {
                's': '2008-01-01',
                'e': '2008-12-31'
            },
            'nodata': -9999
        },
        '16a': {
            'product': 'MCD43A3',
            'version': 'v6',
            'parameter': 'land',
            'resolution': 'daily',
            'variable': 'AlbedoBSA',
            'bbox': {
                'w': -5.0,
                'n': 30.0,
                'e': 5.0,
                's': 25.0
            },
            'period': {
                's': '2008-01-01',
                'e': '2008-01-02'
            },
            'nodata': -9999
        },
        '16b': {
            'product': 'MCD43A3',
            'version': 'v6',
            'parameter': 'land',
            'resolution': 'daily',
            'variable': 'AlbedoWSA',
            'bbox': {
                'w': -5.0,
                'n': 30.0,
                'e': 5.0,
                's': 25.0
            },
            'period': {
                's': '2008-01-01',
                'e': '2008-01-02'
            },
            'nodata': -9999
        },
        '17a': {
            'product': 'MOD09GQ',
            'version': 'v6',
            'parameter': 'land',
            'resolution': 'daily',
            'variable': 'REFb01',
            'bbox': {
                'w': -5.0,
                'n': 30.0,
                'e': 5.0,
                's': 25.0
            },
            'period': {
                's': '2008-01-01',
                'e': '2008-01-02'
            },
            'nodata': -9999
        },
        '17b': {
            'product': 'MOD09GQ',
            'version': 'v6',
            'parameter': 'land',
            'resolution': 'daily',
            'variable': 'REFb02',
            'bbox': {
                'w': -5.0,
                'n': 30.0,
                'e': 5.0,
                's': 25.0
            },
            'period': {
                's': '2008-01-01',
                'e': '2008-01-02'
            },
            'nodata': -9999
        },
        '18a': {
            'product': 'MOD10A2',
            'version': 'v6',
            'parameter': 'land',
            'resolution': 'eight_daily',
            'variable': 'SnowFrac',
            'bbox': {
                'w': -5.0,
                'n': 30.0,
                'e': 5.0,
                's': 25.0
            },
            'period': {
                's': '2008-01-01',
                'e': '2008-01-09'
            },
            'nodata': -9999
        },
        '18b': {
            'product': 'MOD10A2',
            'version': 'v6',
            'parameter': 'land',
            'resolution': 'eight_daily',
            'variable': 'SnowExt',
            'bbox': {
                'w': -5.0,
                'n': 30.0,
                'e': 5.0,
                's': 25.0
            },
            'period': {
                's': '2008-01-01',
                'e': '2008-01-09'
            },
            'nodata': -9999
        },
        '19a': {
            'product': 'MOD11A2',
            'version': 'v6',
            'parameter': 'land',
            'resolution': 'eight_daily',
            'variable': 'LSTday',
            'bbox': {
                'w': -5.0,
                'n': 30.0,
                'e': 5.0,
                's': 25.0
            },
            'period': {
                's': '2008-01-01',
                'e': '2008-01-09'
            },
            'nodata': -9999
        },
        '19b': {
            'product': 'MOD11A2',
            'version': 'v6',
            'parameter': 'land',
            'resolution': 'eight_daily',
            'variable': 'LSTnight',
            'bbox': {
                'w': -5.0,
                'n': 30.0,
                'e': 5.0,
                's': 25.0
            },
            'period': {
                's': '2008-01-01',
                'e': '2008-01-09'
            },
            'nodata': -9999
        },
        '20a': {
            'product': 'MOD13Q1',
            'version': 'v6',
            'parameter': 'land',
            'resolution': 'sixteen_daily',
            'variable': 'NDVI',
            'bbox': {
                'w': -5.0,
                'n': 30.0,
                'e': 5.0,
                's': 25.0
            },
            'period': {
                's': '2008-01-01',
                'e': '2008-01-17'
            },
            'nodata': -9999
        },
        '21a': {
            'product': 'MOD15A2H',
            'version': 'v6',
            'parameter': 'land',
            'resolution': 'eight_daily',
            'variable': 'Fpar',
            'bbox': {
                'w': -5.0,
                'n': 30.0,
                'e': 5.0,
                's': 25.0
            },
            'period': {
                's': '2008-01-01',
                'e': '2008-01-09'
            },
            'nodata': -9999
        },
        '21b': {
            'product': 'MOD15A2H',
            'version': 'v6',
            'parameter': 'land',
            'resolution': 'eight_daily',
            'variable': 'Lai',
            'bbox': {
                'w': -5.0,
                'n': 30.0,
                'e': 5.0,
                's': 25.0
            },
            'period': {
                's': '2008-01-01',
                'e': '2008-01-09'
            },
            'nodata': -9999
        },
        '22a': {
            'product': 'MOD16A2',
            'version': 'v6',
            'parameter': 'evapotranspiration',
            'resolution': 'eight_daily',
            'variable': 'ETA',
            'bbox': {
                'w': -5.0,
                'n': 30.0,
                'e': 5.0,
                's': 25.0
            },
            'period': {
                's': '2008-01-01',
                'e': '2008-01-09'
            },
            'nodata': -9999
        },
        '22b': {
            'product': 'MOD16A2',
            'version': 'v6',
            'parameter': 'evapotranspiration',
            'resolution': 'eight_daily',
            'variable': 'ETP',
            'bbox': {
                'w': -5.0,
                'n': 30.0,
                'e': 5.0,
                's': 25.0
            },
            'period': {
                's': '2008-01-01',
                'e': '2008-01-09'
            },
            'nodata': -9999
        },
        '23a': {
            'product': 'MOD17A2H',
            'version': 'v6',
            'parameter': 'land',
            'resolution': 'eight_daily',
            'variable': 'GPP',
            'bbox': {
                'w': -5.0,
                'n': 30.0,
                'e': 5.0,
                's': 25.0
            },
            'period': {
                's': '2008-01-01',
                'e': '2008-01-09'
            },
            'nodata': -9999
        },
        '24a': {
            'product': 'MYD13',
            'version': 'v6',
            'parameter': 'land',
            'resolution': 'sixteen_daily',
            'variable': 'NDVI',
            'bbox': {
                'w': -5.0,
                'n': 30.0,
                'e': 5.0,
                's': 25.0
            },
            'period': {
                's': '2008-01-01',
                'e': '2008-01-18'
            },
            'nodata': -9999
        },
        # TODO, 20200207, QPan, ex_PROBAV_HDF5, Docker
        #  GDAL and libhdf5 version
        #  https://github.com/OSGeo/gdal/issues/1428
        # '25a': {
        #     'product': 'PROBAV',
        #     'version': 'v1.01',
        #     'parameter': 'land',
        #     'resolution': 'daily',
        #     'variable': 'NDVI',
        #     'bbox': {
        #         'w': -5.0,
        #         'n': 30.0,
        #         'e': 5.0,
        #         's': 25.0
        #     },
        #     'period': {
        #         's': '2014-03-12',
        #         'e': '2014-03-13'
        #     },
        #     'nodata': -9999
        # },
        '26a': {
            'product': 'RFE',
            'version': 'v2',
            'parameter': 'precipitation',
            'resolution': 'daily',
            'variable': 'PCP',
            'bbox': {
                'w': -19.0,
                'n': 38.0,
                'e': 55.0,
                's': -35.0
            },
            'period': {
                's': '2008-01-01',
                'e': '2008-01-02'
            },
            'nodata': -9999
        },
        # TODO, 20200129, QPan, SEBS (FEWS)
        #  multiplier: uint16 to float32, 0.01
        '27a': {
            'product': 'SEBS',
            'version': 'v1',
            'parameter': 'energy',
            'resolution': 'monthly',
            'variable': 'ETM',
            'bbox': {
                'w': -19.0,
                'n': 38.0,
                'e': 55.0,
                's': -35.0
            },
            'period': {
                's': '2008-01-01',
                'e': '2008-01-02'
            },
            'nodata': -9999
        },
        # TODO, 20200129, QPan, ex_SoilGrids_BigTIFF, Docker
        #  BDRLOG, CLYPPT, CRFVOL, SLTPPT, SNDPPT
        #  multiplier: ubyte to float32, 0.01 => percent
        # '28a': {
        #     'product': 'SoilGrids',
        #     'version': 'v1',
        #     'parameter': 'soil',
        #     'resolution': '9s',
        #     'variable': 'BDRICM',
        #     'bbox': {
        #         'w': -19.0,
        #         'n': 38.0,
        #         'e': 55.0,
        #         's': -35.0
        #     },
        #     'period': {
        #         's': None,
        #         'e': None
        #     },
        #     'nodata': -9999
        # }
        '29a': {
            'product': 'TRMM',
            'version': 'v7a',
            'parameter': 'precipitation',
            'resolution': 'monthly',
            'variable': 'PCP',
            'bbox': {
                'w': -19.0,
                'n': 38.0,
                'e': 55.0,
                's': -35.0
            },
            'period': {
                's': '2008-01-01',
                'e': '2008-01-02'
            },
            'nodata': -9999
        },
        '30a': {
            'product': 'TWC',
            'version': 'v1',
            'parameter': 'water',
            'resolution': '5m',
            'variable': 'WPL',
            'bbox': {
                'w': -19.0,
                'n': 38.0,
                'e': 55.0,
                's': -35.0
            },
            'period': {
                's': None,
                'e': None
            },
            'nodata': -9999
        }
    }

    dump_to_yaml(path, test_args)
    main(path, test_args)
