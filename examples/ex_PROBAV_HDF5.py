# -*- coding: utf-8 -*-
import inspect
import os

import IHEWAcollect


def main():
    # Caution:
    # A 69618 pixels x 29007 lines x 1 bands Float32 image would be larger than 4GB
    # but this is the largest size a TIFF can be, and BigTIFF is unavailable.
    # Docker, pass!

    path = os.path.join(
        os.getcwd(),
        os.path.dirname(
            inspect.getfile(
                inspect.currentframe()))
    )

    product = 'PROBAV'
    version = 'v1.01'
    parameter = 'land'
    resolution = 'daily'
    variable = 'NDVI'
    bbox = {
        'w': 118.0642363480000085,
        'n': 10.4715946960000679,
        'e': 126.6049655970000458,
        's': 4.5872944970000731
    }
    period = {
        's': '2014-03-12',
        'e': '2014-03-13'
    }
    nodata = -9999

    IHEWAcollect.Download(workspace=path,
                          product=product,
                          version=version,
                          parameter=parameter,
                          resolution=resolution,
                          variable=variable,
                          bbox=bbox,
                          period=period,
                          nodata=nodata,
                          is_status=False)


if __name__ == "__main__":
    main()
