# -*- coding: utf-8 -*-
"""

"""
import os

import numpy as np

try:
    # from osgeo import gdal, osr, gdalconst
    from osgeo import gdal
except ImportError:
    import gdal


def main():
    """
    **main**

    **Examples:**
    ::

        # Define the output name
        name_out = os.path.join(
            output_folder,
            'ETmonitor_mm_monthly_%d_%02d_01_part1.tif' %(year, month)
        )

        # find path to the executable
        fullCmd = '{exe} {para1} {para2} {para3} {para4} {dir} {fname}'.format(
            exe='gdalwarp',
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
            para4='-t_srs EPSG:4326 -of GTiff',
            dir=file_dir_out,
            fname=name_out
        )  # -r {nearest}

        process = subprocess.Popen(fullCmd)
        process.wait()
    """
    output_folder = r"J:\Tim\ETmonitor"
    for year in range(2008, 2014):
        ETmonitor_tot = np.ones([18000, 31200]) * np.nan
        Distance = 926.625
        for month in range(1, 12):
            for htile in range(7, 33):
                for vtile in range(0, 15):
                    file_name = "ETmonitor_%d_%02d_h%02dv%02d.tif" % (
                        year, month, htile, vtile)
                    total_name = os.path.join(output_folder, file_name)
                    if os.path.exists(total_name):
                        dest = gdal.Open(total_name)
                        data = dest.GetRasterBand(1).ReadAsArray()
                        Hstart = (htile - 7) * 1200
                        Vstart = vtile * 1200
                        ETmonitor_tot[Vstart:Vstart + 1200, Hstart:Hstart + 1200] = data

            ETmonitor_tot[ETmonitor_tot < 0] = np.nan
            file_name = "ET_ETmonitor_mm-month_%d_%02d_01.tif" % (year, month)
            file_dir_out = os.path.join(output_folder, file_name)

            # Make geotiff file
            driver = gdal.GetDriverByName("GTiff")
            dst_ds = driver.Create(file_dir_out, ETmonitor_tot.shape[1],
                                   ETmonitor_tot.shape[0], 1, gdal.GDT_Float32,
                                   ['COMPRESS=LZW'])

            proj = 'PROJCS["unnamed",' \
                   'GEOGCS["Unknown datum based upon the custom spheroid",' \
                   'DATUM["Not specified (based on custom spheroid)",' \
                   'SPHEROID["Custom spheroid",6371007.181,0]],' \
                   'PRIMEM["Greenwich",0],' \
                   'UNIT["degree",0.0174532925199433]],' \
                   'PROJECTION["Sinusoidal"],' \
                   'PARAMETER["longitude_of_center",0],' \
                   'PARAMETER["false_easting",0],' \
                   'PARAMETER["false_northing",0],' \
                   'UNIT["Meter",1]]'
            x1 = (7 - 18) * 1200 * Distance
            x4 = (0 - 9) * 1200 * -1 * Distance
            geo = [x1, Distance, 0.0, x4, 0.0, -Distance]
            geo_t = tuple(geo)
            dst_ds.SetProjection(proj)

            dst_ds.GetRasterBand(1).SetNoDataValue(-9999)
            dst_ds.SetGeoTransform(geo_t)
            dst_ds.GetRasterBand(1).WriteArray(0.1 * ETmonitor_tot)
            dst_ds = None
