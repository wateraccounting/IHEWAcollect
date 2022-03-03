import numpy as np
import requests
from bs4 import BeautifulSoup
import os
import re

def start_download_tiles(date, file,
                         url_server, url_dir, username, password,
                         latlim, lonlim, fname_r, file_r, save_list, output_folder) -> tuple:
    """Get tile name
    """
    url = '{sr}{dr}'.format(sr=url_server, dr=url_dir)
    # print('url: "{f}"'.format(f=url))

    # latmin = int(np.floor((90.0 - latlim[1]) / 10.))
    # latmax = int(np.ceil((90.0 - latlim[0]) / 10.))
    # lonmin = int(np.floor((180.0 + lonlim[0]) / 10.)-1)
    # lonmax = int(np.ceil((180.0 + lonlim[1]) / 10.))

    # if(latmin==latmax): latmax = latmin+1
    # if(lonmin==lonmax): lonmax = lonmin+1

    # Define which MODIS tiles are required
    TilesVertical, TilesHorizontal = Get_tiles_from_txt(output_folder, "", latlim, lonlim)
    # print('Tiles :',TilesVertical, TilesHorizontal)

    lat_steps = range(int(TilesVertical[0]), int(TilesVertical[1])+1, 1)
    lon_steps = range(int(TilesHorizontal[0]), int(TilesHorizontal[1])+1, 1)

    # lat_steps = range(latmin, latmax, 1)
    # lon_steps = range(lonmin, lonmax, 1)
    # print(lat_steps, lon_steps)

    fnames = []
    files = []
    lonlat = []
    for lon_step in lon_steps:
        string_long = 'h{:02d}'.format(lon_step)
        for lat_step in lat_steps:
            string_lat = 'v{:02d}'.format(lat_step)
            lonlat.append([lon_step * 10.0 - 180.0, 90.0 - lat_step * 10.0])

            ctime = start_download_scan(url, file, username, password,
                                        string_lat, string_long, save_list)

            if ctime != '':
                fnames.append(fname_r.format(dtime=date, ctime=ctime,
                                             lat=string_lat, lon=string_long))
                files.append(file_r.format(dtime=date, ctime=ctime,
                                           lat=string_lat, lon=string_long))

    return fnames, files, lonlat

def start_download_scan(url, file, username, password, lat, lon, save_list) -> tuple:
    """Scan tile name
    """
    ctime = ''

    #Connect to server
    conn = requests.get(url)
    soup = BeautifulSoup(conn.content, "html.parser")
    # if __this.conf['is_save_list']:
    if (save_list):
        # Scan available data on the server
        # Curl or Menually to CSR-v3.1.html
        with open(file, 'w') as fp:
            conn = requests.get(url)
            fp.write(conn.text)

    # # Scan available data on local drive
    # conn = open(file, 'r', encoding='UTF8')
    # soup = BeautifulSoup(conn, "html.parser")

    for ele in soup.findAll('a', attrs={'href': re.compile('(?i)(hdf)$')}):
        # print('{lon}{lat}'.format(lat=lat, lon=lon) == ele['href'].split('.')[-4],
        #       ele)
        if '{lon}{lat}'.format(lat=lat, lon=lon) == ele['href'].split('.')[-4]:
            ctime = ele['href'].split('.')[-2]
    
    return ctime

def Get_tiles_from_txt(output_folder, hdf_library, latlim, lonlim):

    import urllib

    # Download list (txt file on the internet) which includes the lat and lon information of the MODIS tiles
    nameDownloadtext = 'https://modis-land.gsfc.nasa.gov/pdf/sn_gring_10deg.txt'
    file_nametext = os.path.join(output_folder, nameDownloadtext.split('/')[-1])
    if hdf_library == None:
        Path_to_txt_file = ""
    else:
        Path_to_txt_file = hdf_library
        file_nametext = os.path.join(Path_to_txt_file, nameDownloadtext.split('/')[-1])
    if not os.path.exists(file_nametext):
        try:
            try:
                urllib.urlretrieve(nameDownloadtext, file_nametext)
            except:
                data = urllib.request.urlopen(nameDownloadtext).read()
                with open(file_nametext, "wb") as fp:
                    fp.write(data)
        except:
            from requests.packages.urllib3.exceptions import InsecureRequestWarning
            requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
            with open(file_nametext, "wb") as fp:
                data = requests.get(nameDownloadtext, verify=False)
                fp.write(data.content)

    # Open text file with tiles which is downloaded before
    tiletext=np.genfromtxt(file_nametext,skip_header=7,skip_footer=1,usecols=(0,1,2,3,4,5,6,7,8,9))
    tiletext2=tiletext[tiletext[:,2]>=-900,:]

    # This function converts the values in the text file into horizontal and vertical number of the tiles which must be downloaded to cover the extent defined by the user
    TilesVertical, TilesHorizontal = Tiles_to_download(tiletext2=tiletext2,lonlim1=lonlim,latlim1=latlim)

    return(TilesVertical, TilesHorizontal)

def Tiles_to_download(tiletext2,lonlim1,latlim1):
    '''
    Defines the MODIS tiles that must be downloaded in order to cover the latitude and longitude limits

    Keywords arguments:
    tiletext2 -- 'C:/file/to/path/' to path of the txt file with all the MODIS tiles extents
    lonlim1 -- [ymin, ymax] (longitude limits of the chunk or whole image)
    latlim1 -- [ymin, ymax] (latitude limits of the chunk or whole image)
    '''
    # calculate min and max longitude and latitude
    # lat down    lat up      lon left     lon right
    tiletextExtremes = np.empty([len(tiletext2),6])
    tiletextExtremes[:,0] = tiletext2[:,0]
    tiletextExtremes[:,1] = tiletext2[:,1]
    tiletextExtremes[:,2] = np.minimum(tiletext2[:,3], tiletext2[:,9])
    tiletextExtremes[:,3] = np.maximum(tiletext2[:,5], tiletext2[:,7])
    tiletextExtremes[:,4] = np.minimum(tiletext2[:,2], tiletext2[:,4])
    tiletextExtremes[:,5] = np.maximum(tiletext2[:,6], tiletext2[:,8])

    # Define the upper left tile
    latlimtiles1UL = tiletextExtremes[np.logical_and(tiletextExtremes[:,2] <= latlim1[1], tiletextExtremes[:,3] >= latlim1[1])]#tiletext2[:,3]>=latlim[0],tiletext2[:,4]>=latlim[0],tiletext2[:,5]>=latlim[0],tiletext2[:,6]>=latlim[0],tiletext2[:,7]>=latlim[0]))]
    latlimtilesUL = latlimtiles1UL[np.logical_and(latlimtiles1UL[:,4] <= lonlim1[0], latlimtiles1UL[:,5] >= lonlim1[0])]

    # Define the lower right tile
    latlimtiles1LR = tiletextExtremes[np.logical_and(tiletextExtremes[:,2] <= latlim1[0], tiletextExtremes[:,3] >= latlim1[0])]#tiletext2[:,3]>=latlim[0],tiletext2[:,4]>=latlim[0],tiletext2[:,5]>=latlim[0],tiletext2[:,6]>=latlim[0],tiletext2[:,7]>=latlim[0]))]
    latlimtilesLR = latlimtiles1LR[np.logical_and(latlimtiles1LR[:,4]<=lonlim1[1],latlimtiles1LR[:,5]>=lonlim1[1])]

    # Define the total tile
    TotalTiles = np.vstack([latlimtilesUL, latlimtilesLR])

    # Find the minimum horizontal and vertical tile value and the maximum horizontal and vertical tile value
    TilesVertical = [TotalTiles[:,0].min(), TotalTiles[:,0].max()]
    TilesHorizontal = [TotalTiles[:,1].min(), TotalTiles[:,1].max()]
    return(TilesVertical, TilesHorizontal)