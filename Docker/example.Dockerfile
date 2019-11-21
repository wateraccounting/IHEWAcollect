# docker build -t wapor/jupyter .
# docker run -it --name wapor -p 8888:8888 -v /d/20190904-Training_Oct:/notebooks wapor/jupyter
# docker system prune -f && docker volume prune -f && docker container prune -f

FROM osgeo/gdal:ubuntu-full-latest
# /usr/bin
# /usr/include
# /usr/lib
# /usr/lib/python3/dist-packages
#
# /usr/local/bin
# /usr/local/include
# /usr/local/lib

MAINTAINER "Quan Pan" <quanpan302@hotmail.com>

# ADD ./tzdata.sh /tzdata.sh
# RUN ["chmod", "+x", "/tzdata.sh"]
# RUN apt-get update -y
# RUN bash /tzdata.sh

ENV LAST_UPDATE=2019-09-19
# 2019-09-23
# sha256:8f963a034301d89293ed63d390af1666fd5b4e8f807598f994b5cd95602996ad
# GDAL 3.1.0dev-650fc42f344a6a4c65f11eefc47c473e9b445a68, released 2019/08/25
# https://github.com/OSGeo/gdal/commit/650fc42f344a6a4c65f11eefc47c473e9b445a68

RUN apt-get update && \
    apt-get upgrade -y

# Tools necessary for installing and configuring Ubuntu
RUN apt-get install -y \
    apt-utils \
    locales \
    tzdata

# Timezone
RUN echo "Europe/Amsterdam" | tee /etc/timezone && \
    ln -fs /usr/share/zoneinfo/Europe/Amsterdam /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata

# Locale with UTF-8 support
RUN echo en_US.UTF-8 UTF-8 >> /etc/locale.gen && \
    locale-gen && \
    update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

# Install basic tools
RUN apt-get install -y \
    software-properties-common \
    bash-completion \
    curl \
    wget \
    unzip \
    vim \
    git \
    build-essential \
    cmake \
    sqlite3

# Configure bash_completion
RUN echo 'defshell -bash' >> /root/.screenrc
RUN echo 'if [ -f /etc/bash_completion ] && ! shopt -oq posix; then' >> /root/.bashrc && \
    echo '    . /etc/bash_completion' >> /root/.bashrc && \
    echo 'fi' >> /root/.bashrc

# Install basic libraries
RUN apt-get install -y \
    libspatialite-dev \
    libpq-dev \
    libcurl4-gnutls-dev \
    libgnutls28-dev \
    libproj-dev \
    libxml2-dev \
    libgeos-dev \
    libnetcdf-dev \
    libpoppler-dev \
    libspatialite-dev \
    libhdf4-alt-dev \
    libhdf5-serial-dev

# Install python libraries
RUN apt-get install -y \
    python3-dev \
    python3-pip \
    python3-scipy \
    python3-numpy \
    python3-pandas

# Install python dependencies
RUN pip3 install \
    requests \
    pytest \
    netcdf4 \
    shapely \
    pyshp \
    rasterio \
    "dask[complete]" \
    "dask-ml[complete]" \
    xarray \
    pyproj \
    pycurl \
    paramiko \
    jupyterlab

# Workspace
RUN mkdir /notebooks

# CMD gdalinfo --version
CMD jupyter notebook --no-browser --allow-root --ip 0.0.0.0 --port 8888 /notebooks
