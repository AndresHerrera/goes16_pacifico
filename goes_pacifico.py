import os
import GOES
import numpy as np
import datetime as dt
import pyproj as pyproj
from global_func import list_files_by_mtime, purge_folder
from nc_utils import save_as_nc
from pyresample import utils
from pyresample.geometry import SwathDefinition
from pyresample.kd_tree import resample_nearest
from dotenv import load_dotenv
load_dotenv()

# Define the product and channel
product = 'ABI-L2-CMIPF'
channelp = ['13'] 
pathOut = os.getenv('PATH_OUT')
geoserverPath = os.getenv('GEOSERVER_PATH')
filenameLatest = os.getenv('FILENAME_OUT')
extIn ='.nc'

# Domain for Colombia
domain = [-90.0,-65.0,-5,13]

# Get date and actual time
now = dt.datetime.now()
date_str = now.strftime("%Y%m%d")
new_time = now - dt.timedelta(minutes=15)
formatted_time = new_time.strftime("%H%M")
hour = now.strftime("%H%M")

timeIni = f'{date_str}-{formatted_time}00'
timeEnd = f'{date_str}-{hour}59'

print(f"--------- Timestamp ---------")
print(f'Ini: {timeIni}')
print(f'End: {timeEnd}')

print(f"--------- Download data ---------")
# Download GOES file
flist = GOES.download('goes16', product,
             DateTimeIni = timeIni, DateTimeFin = timeEnd, 
             channel = channelp , path_out=pathOut)

sorted_files = list_files_by_mtime(pathOut,extIn)

if(len(sorted_files)<0):
  print(f"No existen archivos en {pathOut}")
else:
  print(f"Latest {extIn} file {sorted_files[0]} ")

  print(f"Files in folder: {len(sorted_files)}")
  # Keep only the latest hour
  if(len(sorted_files)>=4):
    print(f"--------- Purge folder ---------")
    if(purge_folder(pathOut,extIn,4)):
      sorted_files = list_files_by_mtime(pathOut,extIn)
      print("Folder purged done!")
      print(f"Files in folder: {len(sorted_files)}")
# Reads the file
  ds = GOES.open_dataset(sorted_files[0])
# Gets image with the coordinates of center of their pixels.
  CMI, LonCen, LatCen = ds.image('CMI', lonlat='center', domain=domain)
# Image stats  
  sat = ds.attribute('platform_ID')
  band = ds.variable('band_id').data[0]
  wl = ds.variable('band_wavelength').data[0]
  standard_name = CMI.standard_name
  long_name = CMI.long_name
  units = CMI.units
  time_bounds = CMI.time_bounds
  
  print(f"--------- Image stats ---------")
  print(f"Platform id: {sat}")
  print(f"Band id: {band}")
  print(f"Band wavelength id: {wl}")
  print(f"Standard name: {standard_name}")
  print(f"Long name: {long_name}")
  print(f"Units: {units}")
  #print(time_bounds)
  
  print(f"--------- Reproject file ---------")
  
  # Creates a grid map with cylindrical equidistant projection and 2 km of spatial resolution.
  LonCenCyl, LatCenCyl = GOES.create_gridmap(domain, PixResol=2.0)
  
  # Defile projection
  Prj = pyproj.Proj('+proj=eqc +lat_ts=0 +lat_0=0 +lon_0=0 +x_0=0 +y_0=0 +a=6378.137 +b=6378.137 +units=km')
  AreaID = 'cyl'
  AreaName = 'cyl'
  ProjID = 'cyl'
  Proj4Args = '+proj=eqc +lat_ts=0 +lat_0=0 +lon_0=0 +x_0=0 +y_0=0 +a=6378.137 +b=6378.137 +units=km'

  ny, nx = LonCenCyl.data.shape
  SW = Prj(LonCenCyl.data.min(), LatCenCyl.data.min())
  NE = Prj(LonCenCyl.data.max(), LatCenCyl.data.max())
  area_extent = [SW[0], SW[1], NE[0], NE[1]]

  AreaDef = utils.get_area_def(AreaID, AreaName, ProjID, Proj4Args, nx, ny, area_extent)

  SwathDef = SwathDefinition(lons=LonCen.data, lats=LatCen.data)
  CMICyl = resample_nearest(SwathDef, CMI.data, AreaDef, radius_of_influence=6000,
                            fill_value=np.nan, epsilon=3, reduce_data=True)
  del CMI, LonCen, LatCen, SwathDef
  
  dict = {'name':'CMI',
        'standard_name':standard_name,
        'long_name':long_name,
        'units':units,
        'axis':'YX'}

  LonCenCyl1D = LonCenCyl.data[0,:] # Longitude of pixel center in 1D
  LatCenCyl1D = LatCenCyl.data[:,0] # Latitude of pixel center in 1D
  sst = time_bounds.data[0] # scan start time
  
  save_as_nc(CMICyl, dict, LonCenCyl1D, LatCenCyl1D, sst, os.path.join(geoserverPath,filenameLatest))
  