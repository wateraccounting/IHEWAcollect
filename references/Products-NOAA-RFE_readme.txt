#
# This is the README file for the Rainfall Estimator (RFE) for data over Africa.
#

OVERVIEW:

- The RFE algorithm is based on the PingPing Xie method currently being employed
as an operational product at the NOAA/Climate Prediction Center in association
with USAID/FEWS-NET. Maps of rainfall estimates over varying timescales may be
found at:

http://www.cpc.ncep.noaa.gov/products/international/africa/africa.shtml



Caveats with Data: Updated April, 2010

- There are some days in 2005 where daily RFE estimates exceed
the 300mm threshold for a limited number of pixels. Please include any
conditional statements to remove and/or substitute these pixels upon reading
the binary data.


1.  filename

    all_products.bin.YYYYMMDD

    YYYY == 4 digit year
    MM   == month
    DD   == date

2.  description of the data

    content:
    rain  ==   daily precipitation analysis by merging
               GTS gauge observations and  3 kinds of satellite estimates.
               (GPI,SSM/I and AMSU) Units are in millimeters (mm)

    Data files are written in binary data format and consist of one record (one
    array) of floating point rainfall estimates in mm (after unzipping).  Each array
    equals 751*801 elements, corresponding to 751 pixels in the x direction, and 801 pixels
    in the y direction.  After reshaping to a 0.1 degree grid, this will yield a
    spatial domain spanning -40S to 40N in latitude, and -20W to 55E in longitude
    encompassing the Africa continent.  Missing data is denoted as -999.0.


3.  example program

c     program     :     example.f
c     objective   :     to read the daily estimates
c
      dimension    rain(751,801)
c
c     1.  to open the data file
c
      open  (unit=10,file='all_products.bin.20000601',
     #       access='direct',status='readonly',recl=751*801)
c
c     2.  to read the data
c
      read (10,rec=1)   rain
c
      stop
      end
