# -*- coding: utf-8 -*-
import inspect
import os

import IHEWAcollect


def main():

    path = os.path.join(
        os.getcwd(),
        os.path.dirname(
            inspect.getfile(
                inspect.currentframe()))
    )

    product = 'MOD16A2'
    version = 'v6'
    parameter = 'evapotranspiration'
    resolution = 'eight_daily'
    variable = 'ETA'
    bbox = {
        'w': 118.0642363480000085,
        'n': 10.4715946960000679,
        'e': 126.6049655970000458,
        's': 4.5872944970000731
    }
    period = {
        's': '2008-01-01',
        'e': '2008-01-09'
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
