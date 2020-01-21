import os
import inspect

from IHEWAcollect.download import Download


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

    product = 'ETmonitor'
    version = 'v1'
    parameter = 'evapotranspiration'
    resolution = 'monthly'
    variable = 'ETA'
    # variable = 'ETP'
    bbox = {
        'w': -19.0,
        's': -35.0,
        'e': 55.0,
        'n': 38.0
    }
    period = {
        's': '2008-01-01',
        'e': '2008-01-31'
    }

    download = Download(workspace=path,
                        product=product,
                        version=version,
                        parameter=parameter,
                        resolution=resolution,
                        variable=variable,
                        bbox=bbox,
                        period=period,
                        NaN=-9999,
                        is_status=False)


if __name__ == "__main__":
    main()
