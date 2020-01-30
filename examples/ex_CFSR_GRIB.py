import os
import inspect

import IHEWAcollect


def main():
    # Caution:
    # dec_jpeg2000: Unable to open JPEG2000 image within GRIB file.
    # Docker, pass!

    path = os.path.join(
        os.getcwd(),
        os.path.dirname(
            inspect.getfile(
                inspect.currentframe()))
    )

    product = 'CFSR'
    version = 'v1'
    parameter = 'radiation'
    resolution = 'daily'
    variable = 'dlwsfc'
    bbox = {
        'w': -19.0,
        'n': 38.0,
        'e': 55.0,
        's': -35.0
    }
    period = {
        's': '2007-01-01',
        'e': '2007-01-02'
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
