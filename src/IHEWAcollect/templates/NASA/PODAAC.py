# -*- coding: utf-8 -*-
# ! /usr/bin/env python
#
# a skeleton script to download a set of L2/L2P file using OPeNDAP.
#
#
#   2017.11.26  Y. Jiang, Ed Armstrong version 0

##################################
# user parameters to be editted: #
##################################

# Caution: This is a Python script, and Python takes indentation seriously.
# DO NOT CHANGE INDENTATION OF ANY LINE BELOW!
#
# Here is the list of parameters
#
#  -h, --help            show this help message and exit
#  -x SHORTNAME, --shortname=SHORTNAME
#                        product short name
#  -s DATE0, --start=DATE0
#                        start date: Format yyyymmdd (eg. -s 20140502 for May
#                        2, 2014) [default: yesterday 20171130]
#  -f DATE1, --finish=DATE1
#                        finish date: Format yyyymmdd (eg. -f 20140502 for May
#                        2, 2014) [default: today 20171201]
#  -b BOX, --subset=BOX  limit the domain to a box given by
#                        lon_min,lon_max,lat_min,lat_max (eg. -r -140 -110 20
#                        30) [default: (-180.0, 180.0, -90.0, 90.0)]
#
# Example:
# % ./subset_dataset_l2.py -s 20100101 -f 20100201 -b -140 -110 20 30 -x TMI-REMSS-L2P-v4
# Subset the data from 1 Jan 2010 to 1 Feb 2010 in a box from -140 to -110 degrees longitude and 20 to 30 degrees latitude
# for shortName TMI-REMSS-L2P-v4

import os
import sys
import time
from datetime import date, timedelta
from math import ceil, floor
from optparse import OptionParser
from xml.dom import minidom

import numpy as np
from pydap.client import open_url

if sys.version_info >= (3, 0):
    import subprocess
    import urllib.request
else:
    import commands
    import urllib

#####################
# Global Parameters #
#####################

itemsPerPage = 10
PODAAC_WEB = 'https://podaac.jpl.nasa.gov'


###############
# subroutines #
###############
def yearday(day, month, year):
    months = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if isLeap(year):
        months[2] = 29
    for m in range(month):
        day = day + months[m]
    return (day)


def today():
    import datetime
    todays = datetime.date.today()
    return str(todays.year) + str(todays.month).zfill(2) + str(todays.day).zfill(2)


def yesterday():
    import datetime
    yesterdays = datetime.date.today() - timedelta(days=1)
    return str(yesterdays.year) + str(yesterdays.month).zfill(2) + str(
        yesterdays.day).zfill(2)


# input parameters handling
def parseoptions():
    usage = "Usage: %prog [options]"
    parser = OptionParser(usage)
    parser.add_option("-x", "--shortname", help="product short name", dest="shortname")

    parser.add_option("-s", "--start",
                      help="start date: Format yyyymmdd (eg. -s 20140502 for May 2, 2014) [default: yesterday %default]",
                      dest="date0", default=yesterday())
    parser.add_option("-f", "--finish",
                      help="finish date: Format yyyymmdd (eg. -f 20140502 for May 2, 2014) [default: today %default]",
                      dest="date1", default=today())
    parser.add_option("-b", "--subset",
                      help="limit the domain to a box given by lon_min,lon_max,lat_min,lat_max (eg. -r -140 -110 20 30) [default: %default]",
                      type="float", nargs=4, dest="box",
                      default=(-180., 180., -90., 90.))

    # Parse command line arguments
    (options, args) = parser.parse_args()

    # print help if no arguments are given
    if (len(sys.argv) == 1):
        parser.print_help()
        exit(-1)

    if options.shortname == None:
        print('\nShortname is required !\nProgram will exit now !\n')
        parser.print_help()
        exit(-1)

    return (options)


def standalone_main():
    # get command line options:

    options = parseoptions()

    shortname = options.shortname

    date0 = options.date0
    if options.date1 == -1:
        date1 = date0
    else:
        date1 = options.date1

    if len(date0) != 8:
        sys.exit(
            '\nStart date should be in format yyyymmdd !\nProgram will exit now !\n')

    if len(date1) != 8:
        sys.exit('\nEnd date should be in format yyyymmdd !\nProgram will exit now !\n')

    year0 = date0[0:4];
    month0 = date0[4:6];
    day0 = date0[6:8];
    year1 = date1[0:4];
    month1 = date1[4:6];
    day1 = date1[6:8];

    timeStr = '&startTime=' + year0 + '-' + month0 + '-' + day0 + '&endTime=' + year1 + '-' + month1 + '-' + day1

    box = list(options.box)

    print('\nPlease wait while program searching for the granules ...\n')

    wsurl = PODAAC_WEB + '/ws/search/granule/?shortName=' + shortname + timeStr + '&itemsPerPage=1&sortBy=timeAsc'
    if sys.version_info >= (3, 0):
        response = urllib.request.urlopen(wsurl)
    else:
        response = urllib.urlopen(wsurl)
    data = response.read()

    if (len(data.splitlines()) == 1):
        sys.exit(
            'No granules found for dataset: ' + shortname + '\nProgram will exit now !\n')

    numGranules = 0
    doc = minidom.parseString(data)
    for arrays in doc.getElementsByTagName('link'):
        names = arrays.getAttribute("title")
        if names == 'OPeNDAP URL':
            numGranules = numGranules + 1
            href = arrays.getAttribute("href")
            # if numGranules > 0:
            #  break

    if numGranules == 0 and len(data.splitlines()) < 30:
        sys.exit(
            'No granules found for dataset: ' + shortname + '\nProgram will exit now !\n')
    elif numGranules == 0 and len(data.splitlines()) > 30:
        sys.exit(
            'No OpenDap access for dataset: ' + shortname + '\nProgram will exit now !\n')

    samplefile = href.rsplit(".", 1)[0] + '.ddx'

    if sys.version_info >= (3, 0):
        doc = minidom.parse(urllib.request.urlopen(samplefile))
    else:
        doc = minidom.parse(urllib.urlopen(samplefile))

    for arrays in doc.getElementsByTagName('Attribute'):
        names = arrays.getAttribute("name")
        if names == 'processing_level':
            for nodes in arrays.getElementsByTagName("value"):
                for cn in nodes.childNodes:
                    plevel = cn.nodeValue

    if ('L2' in plevel) == False:
        print('This script only works for L2/L2P datasets !\n')
        print(
            'Please goto the following link in the PODAAC Forum to download L3/L4 datasets:\n')
        print(
            'https://podaac.jpl.nasa.gov/forum/viewtopic.php?f=85&t=219&sid=6115218902d71b00cfdebc5adb6a2a58\n')
        print('Program will exit now !\n')
        exit(1)

    # ****************************************************************************
    # download size information:
    print(' ')
    print('Longitude range: %f to %f' % (box[0], box[1]))
    print('Latitude range: %f to %f' % (box[2], box[3]))
    print(' ')

    if sys.version_info >= (3, 0):
        r = input('OK to download?  [yes or no]: ')
    else:
        r = raw_input('OK to download?  [yes or no]: ')
    if len(r) == 0 or (r[0] != 'y' and r[0] != 'Y'):
        print('... no download')
        sys.exit(0)

    # Check if curl or wget commands exsit on your computer
    if sys.version_info >= (3, 0):
        status_curl, result = subprocess.getstatusoutput('which curl')
        status_wget, result = subprocess.getstatusoutput('which wget')
    else:
        status_curl, result = commands.getstatusoutput("which curl")
        status_wget, result = commands.getstatusoutput("which wget")

    # main loop:
    start = time.time()
    bmore = 1
    while (bmore > 0):
        if (bmore == 1):
            urllink = PODAAC_WEB + '/ws/search/granule/?shortName=' + shortname + timeStr + '&itemsPerPage=%d&sortBy=timeAsc' % itemsPerPage
        else:
            urllink = PODAAC_WEB + '/ws/search/granule/?shortName=' + shortname + timeStr + '&itemsPerPage=%d&sortBy=timeAsc&startIndex=%d' % (
            itemsPerPage, (bmore - 1) * itemsPerPage)
        bmore = bmore + 1
        if sys.version_info >= (3, 0):
            response = urllib.request.urlopen(urllink)
        else:
            response = urllib.urlopen(urllink)
        data = response.read()
        doc = minidom.parseString(data)

        numGranules = 0
        for arrays in doc.getElementsByTagName('link'):
            names = arrays.getAttribute("title")
            if names == 'OPeNDAP URL':
                numGranules = numGranules + 1
                href = arrays.getAttribute("href")
                ncfile = href.rsplit(".", 1)[0]
                head, tail = os.path.split(ncfile)
                ncout = tail
                if ncout.endswith('.bz2') or ncout.endswith('.gz'):
                    ncout = ncout.rsplit(".", 1)[0]
                ncout = ncout.rsplit(".", 1)[0] + '_subset.' + ncout.rsplit(".", 1)[1]
                dataset = open_url(ncfile)
                lon = dataset['lon']
                lat = dataset['lat']
                selindex = np.where(
                    (lon > box[0]) & (lon < box[1]) & (lat > box[2]) & (lat < box[3]))
                if (len(selindex[0]) > 0 and len(selindex[1]) > 0):
                    nimin, nimax = selindex[1].min(), selindex[1].max()
                    njmin, njmax = selindex[0].min(), selindex[0].max()
                    cmd = ncfile + '.nc?'
                    for item in dataset.keys():
                        if (item == 'lon' or item == 'lat'):
                            index = '[%d:%d][%d:%d]' % (njmin, njmax, nimin, nimax)
                        elif (item == 'time'):
                            index = '[0:0]'
                        else:
                            index = '[0:0][%d:%d][%d:%d]' % (njmin, njmax, nimin, nimax)
                        cmd = cmd + item + index + ','
                    cmd = cmd[0:(len(cmd) - 1)]  # remove the extra "," at the end.

                    if status_curl == 0:
                        cmd = 'curl -g "' + cmd + '" -o ' + ncout
                    elif status_wget == 0:
                        cmd = 'wget "' + cmd + '" -O ' + ncout
                    else:
                        sys.exit(
                            '\nThe script will need curl or wget on the system, please install them first before running the script !\nProgram will exit now !\n')

                    print(cmd)
                    os.system(cmd)
                    print(ncout + ' download finished !')

        if numGranules < itemsPerPage:
            bmore = 0

    end = time.time()
    print('Time spend = ' + str(end - start) + ' seconds')


if __name__ == "__main__":
    standalone_main()
