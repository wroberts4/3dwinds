from pywinds.wind_functions import velocity, vu, lat_long, displacements, area, wind_info
from datetime import datetime
from pyproj import Geod, Proj
from xarray import DataArray
from collections import OrderedDict
import numpy as np
import glob
import os
import sys


print(sys.executable)
start = datetime.utcnow()
file_name = 'in.flo'
lat_0 = 60
lon_0 = 0
i_in = None
j_in = None
pixel_size = 4000
center = (90, 0)
shape = None
earth_geod = 'WGS84'
image_geod = 'WGS84'
save_data = False
area_extent = tuple(reversed((-2000000.0, 1429327.9172, 2000000.0, 5429327.9172)))

lat, long, speed, angle, v, u = wind_info(lat_0, lon_0, 100, displacement_data='in.flo', i=i_in, j=j_in, pixel_size=pixel_size, center=center,
              earth_geod=earth_geod, image_geod=image_geod, save_data=save_data).transpose().reshape((6, 1000, 1000))
print(lat[1, 5])
# output_velocity = velocity(lat_0, lon_0, 100, displacement_data='in.flo', i=i_in, j=j_in, pixel_size=pixel_size,
#                            center=center, earth_geod=earth_geod, image_geod=image_geod, save_data=save_data)
# print('speed:', '{0} m/sec, {1}°'.format(*output_velocity[:, 0, 0]))
#
# output_vu = vu(lat_0, lon_0, 100, displacement_data=file_name, i=i_in, j=j_in, pixel_size=pixel_size, center=center,
#                     shape=shape, earth_geod=earth_geod, image_geod=image_geod, save_data=save_data)
# print('(v, u):', '({0} m/sec, {1} m/sec)'.format(*output_vu[:, 0, 0]))
#
# area_def = area(lat_0, lon_0, displacement_data=file_name, pixel_size=10000, center=center, image_geod=image_geod)
# new_shape = (area_def.height, area_def.width)
# print(area_def)
#
# displacement = displacements(displacement_data=file_name, shape=shape, save_data=save_data)
# print('displacements:', *displacement[:, 0, 0])
#
# old_lat_long = lat_long(lat_0, lon_0, i=i_in, j=j_in, pixel_size=pixel_size, center=center,
#                         shape=(1000,1000), image_geod=image_geod)
# print('old_lat, old_long:', *old_lat_long[:, 0, 0])
#
new_lat_long = lat_long(lat_0, lon_0, displacement_data=file_name, i=i_in, j=j_in, pixel_size=pixel_size,
                                center=center, shape=(1000,1000), image_geod=image_geod, save_data=save_data)
print('new_lat, new_long:', *new_lat_long[:, 1, 5])

end = datetime.utcnow()
print("Execution seconds: ", (end - start).total_seconds())
# 60 0 --displacement_data test/test_files/test_data_three.flo --projection stere --pixel_size 10:km --center 90,0 --units None --image_geod None --earth_geod None
