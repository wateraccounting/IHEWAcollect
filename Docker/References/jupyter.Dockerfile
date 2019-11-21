# docker build -t qpan/gdal .
# docker run -it --name gdal qpan/gdal bash
# docker system prune -f

FROM osgeo/gdal:ubuntu-full-latest

ADD tzdata.sh /tzdata.sh
RUN ["chmod", "+x", "/tzdata.sh"]
RUN apt-get update -y
RUN bash /tzdata.sh

# Install basic dependencies
RUN apt-get install -y \
    software-properties-common \
    build-essential \
    python3-dev \
    python3-pip \
    python3-scipy \
    python3-numpy \
    python3-pandas \
    libspatialite-dev \
    sqlite3 \
    libpq-dev \
    libcurl4-gnutls-dev \
    libproj-dev \
    libxml2-dev \
    libgeos-dev \
    libnetcdf-dev \
    libpoppler-dev \
    libspatialite-dev \
    libhdf4-alt-dev \
    libhdf5-serial-dev \
    bash-completion \
    cmake \
    vim

# Install python dependencies
RUN pip3 install pytest \
    shapely \
    pyshp \
    rasterio \
    "dask[complete]" \
    "dask-ml[complete]" \
    xarray \
    jupyterlab

RUN mkdir /notebooks

# CMD gdalinfo --version
CMD jupyter notebook --no-browser --ip 0.0.0.0 --port 8888 /notebooks
