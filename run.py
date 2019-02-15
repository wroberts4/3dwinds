# from pywinds.wind_functions import calculate_velocity, v_u_component, compute_lat_long, get_displacements, get_area
from datetime import datetime
from pyproj import Geod, Proj
from xarray import DataArray
from collections import OrderedDict
import numpy as np
import glob


start = datetime.utcnow()
file_name = './pywinds/test/test_files/test_data_one.flo'
lat_0 = 60
lon_0 = 0
i_in = None
j_in = None
pixel_size = 4000
center = (90, 0)
shape = None
earth_geod = 'WGS84'
image_geod = 'WGS84'
save_data=False
area_extent = tuple(reversed((-2000000.0, 1429327.9172, 2000000.0, 5429327.9172)))

print(glob.glob('*.flo'))

# velocity = calculate_velocity(lat_0, lon_0, file_name, i=i_in, j=j_in, area_extent=area_extent, earth_geod=earth_geod,
#                               image_geod=image_geod, save_data=save_data)
# print('speed:', '{0} m/sec, {1}°'.format(*velocity[:, 0, 0]))
#
# v_u = v_u_component(lat_0, lon_0, file_name, i=i_in, j=j_in, pixel_size=pixel_size, center=center,
#                     shape=shape, earth_geod=earth_geod, image_geod=image_geod, save_data=save_data)
# print('(v, u):', '({0} m/sec, {1} m/sec)'.format(*v_u[:, 0, 0]))
#
# displacements, new_shape = get_displacements(file_name, shape=shape, save_data=save_data)
# # np.ndarray.tofile(displacements, 'C:/Users/William/Documents/test')
# # test = np.fromfile('C:/Users/William/Documents/test', dtype=np.float32)
# # test = test.reshape((2, 1000, 1000))
#
# print('displacements:', *displacements[:, 0, 0], new_shape)
#
# old_lat_long = compute_lat_long(lat_0, lon_0, i=i_in, j=j_in, pixel_size=pixel_size, center=center,
#                                 shape=new_shape, image_geod=image_geod, save_data=save_data)
# print('old_lat, old_long:', *old_lat_long[:, 0, 0])
#
# new_lat_long = compute_lat_long(lat_0, lon_0, displacement_data=file_name, i=i_in, j=j_in, pixel_size=pixel_size,
#                                 center=center, shape=new_shape, image_geod=image_geod, save_data=save_data)
# print('new_lat, new_long:', *new_lat_long[:, 0, 0])
#
# area = get_area(lat_0, lon_0, pixel_size=pixel_size, center=center, shape=new_shape, image_geod=image_geod)
# print(area)
#
# end = datetime.utcnow()
# print("Execution seconds: ", (end - start).total_seconds())