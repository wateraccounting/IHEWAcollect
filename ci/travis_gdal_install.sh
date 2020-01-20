#!/bin/bash
#
# originally contributed by @rbuffat to Toblerity/Fiona
set -e

########################################
# PROJ
########################################
# Create build dir if not exists
if [ ! -d "$PROJBUILD" ]; then
  mkdir $PROJBUILD;
fi

if [ ! -d "$PROJINST" ]; then
  mkdir $PROJINST;
fi

ls -l $PROJINST

echo "PROJ VERSION: $PROJVERSION"

if [ ! -d "$PROJINST/gdal-$GDALVERSION/share/proj" ]; then
    cd $PROJBUILD
    wget -q https://download.osgeo.org/proj/proj-$PROJVERSION.tar.gz
    tar -xzf proj-$PROJVERSION.tar.gz
    cd proj-$PROJVERSION
    ./configure --prefix=$PROJINST/gdal-$GDALVERSION
    make -s -j 2
    make install
fi

########################################
# GDAL
########################################
GDALOPTS="  --without-bsb \
            --without-cfitsio \
            --with-curl \
            --without-ecw \
            --with-expat \
            --without-fme \
            --without-gif \
            --with-geos \
            --with-geotiff=internal \
            --without-grass \
            --with-grib \
            --with-hdf4 \
            --with-hdf5 \
            --without-ingres \
            --without-idb \
            --with-jasper \
            --without-jp2mrsid \
            --with-jpeg=internal \
            --without-kakadu \
            --without-libgrass \
            --with-libtiff=internal \
            --without-libtool \
            --with-libz=internal \
            --without-mrsid \
            --without-mysql \
            --with-netcdf \
            --without-odbc \
            --without-ogdi \
            --without-pcraster \
            --without-perl \
            --without-pg \
            --with-png=internal \
            --with-python \
            --without-sde \
            --without-sqlite3 \
            --without-xerces"

# Create build dir if not exists
if [ ! -d "$GDALBUILD" ]; then
  mkdir $GDALBUILD;
fi

if [ ! -d "$GDALINST" ]; then
  mkdir $GDALINST;
fi

ls -l $GDALINST

if [ "$GDALVERSION" = "master" ]; then
    PROJOPT="--with-proj=$GDALINST/gdal-$GDALVERSION"
    cd $GDALBUILD
    git clone --depth 1 https://github.com/OSGeo/gdal gdal-$GDALVERSION
    cd gdal-$GDALVERSION/gdal
    git rev-parse HEAD > newrev.txt
    BUILD=no
    # Only build if nothing cached or if the GDAL revision changed
    if test ! -f $GDALINST/gdal-$GDALVERSION/rev.txt; then
        BUILD=yes
    elif ! diff newrev.txt $GDALINST/gdal-$GDALVERSION/rev.txt >/dev/null; then
        BUILD=yes
    fi
    if test "$BUILD" = "yes"; then
        mkdir -p $GDALINST/gdal-$GDALVERSION
        cp newrev.txt $GDALINST/gdal-$GDALVERSION/rev.txt
        ./configure --prefix=$GDALINST/gdal-$GDALVERSION $GDALOPTS $PROJOPT
        make -s -j 2
        make install

        which python
        cd swig/python
        python setup.py build
        python setup.py install
        python setup.py bdist_egg
    fi

else
    case "$GDALVERSION" in
        3*)
            PROJOPT="--with-proj=$GDALINST/gdal-$GDALVERSION"
            ;;
        2.4*)
            PROJOPT="--with-proj=$GDALINST/gdal-$GDALVERSION"
            ;;
        2.3*)
            PROJOPT="--with-proj=$GDALINST/gdal-$GDALVERSION"
            ;;
        2.2*)
            PROJOPT="--with-static-proj4=$GDALINST/gdal-$GDALVERSION"
            ;;
        2.1*)
            PROJOPT="--with-static-proj4=$GDALINST/gdal-$GDALVERSION"
            ;;
        2.0*)
            PROJOPT="--with-static-proj4=$GDALINST/gdal-$GDALVERSION"
            ;;
        1*)
            PROJOPT="--with-static-proj4=$GDALINST/gdal-$GDALVERSION"
            ;;
    esac

    if [ ! -d "$GDALINST/gdal-$GDALVERSION/share/gdal" ]; then
        cd $GDALBUILD
        gdalver=$(expr "$GDALVERSION" : '\([0-9]*.[0-9]*.[0-9]*\)')
        wget -q http://download.osgeo.org/gdal/$gdalver/gdal-$GDALVERSION.tar.gz
        tar -xzf gdal-$GDALVERSION.tar.gz
        cd gdal-$gdalver
        ./configure --prefix=$GDALINST/gdal-$GDALVERSION $GDALOPTS $PROJOPT
        make -s -j 2
        make install

        which python
        cd swig/python
        python setup.py build
        python setup.py install
        python setup.py bdist_egg
    fi
fi

# Test gdal
echo "=========="
gdalinfo --version
ls $GDALINST
ls $GDALINST/gdal-$GDALVERSION
echo "=========="

# change back to travis build dir
cd $TRAVIS_BUILD_DIR
