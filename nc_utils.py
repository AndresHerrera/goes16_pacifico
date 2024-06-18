import numpy as np
from netCDF4 import Dataset, date2num

def save_as_nc(Field, Dict, LonsCen, LatsCen, DateTimeField, OutputFile):

   # creates netcdf file
   dataset = Dataset(OutputFile, 'w', format='NETCDF4')

   # Dimensions - I recommend keep the same name for the dimensions
   dataset.createDimension('time', None)
   dataset.createDimension('level', None)
   dataset.createDimension('latitude', LatsCen.shape[0])
   dataset.createDimension('longitude', LonsCen.shape[0])

   # Variables
   file_time = dataset.createVariable('time', np.float64, ('time',))
   file_level = dataset.createVariable('level', np.float32, ('level',))
   file_lats = dataset.createVariable('latitude', LatsCen.dtype.type, ('latitude',))
   file_lons = dataset.createVariable('longitude', LonsCen.dtype.type, ('longitude',))
   file_field = dataset.createVariable(Dict['name'], Field.dtype.type, ('latitude','longitude'), zlib=True)

   # Sets variable attributes
   file_time.standard_name = 'time'
   file_time.long_name = 'time'
   file_time.units = 'hours since 2000-1-1 00:00:00'
   file_time.calendar = 'standard'
   file_time.axis = 'T'

   file_level.standard_name = 'level'
   file_level.long_name = 'level'
   file_level.units = 'millibars'
   file_level.positive = 'down'
   file_level.axis = 'Z'

   file_lats.standard_name = 'latitude'
   file_lats.long_name = 'latitude'
   file_lats.units = 'degrees_north'
   file_lats.axis = 'Y'

   file_lons.standard_name = 'longitude'
   file_lons.long_name = 'longitude'
   file_lons.units = 'degrees_east'
   file_lons.axis = 'X'

   file_field.standard_name = Dict['standard_name']
   file_field.long_name = Dict['long_name']
   file_field.units = Dict['units']
   file_field.axis = Dict['axis']

   # Writing variables
   file_time[:] = date2num(DateTimeField, units = file_time.units, calendar = file_time.calendar)
   file_level[:] = 1000.0
   file_lats[:] = LatsCen
   file_lons[:] = LonsCen
   file_field[:,:] = Field

   # Sets global attributes
   dataset.description = 'GOES-16 Satellite'
   dataset.source = 'NOAA-NASA'
   dataset.author = 'Geopesca'
   dataset.close()
   
   print(f"Save nc file: {OutputFile}")