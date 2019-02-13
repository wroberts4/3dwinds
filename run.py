from pywinds.wind_functions import calculate_velocity, u_v_component, compute_lat_long, get_displacements, get_area
from datetime import datetime
from pyproj import Geod, Proj
from xarray import DataArray
from collections import OrderedDict
import numpy as np


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

velocity = calculate_velocity(lat_0, lon_0, file_name, i=i_in, j=j_in, pixel_size=pixel_size, center=center,
                              shape=shape, earth_geod=earth_geod, image_geod=image_geod, save_data=save_data)
print('speed:', '{0} m/sec, {1}°'.format(*velocity[:, 0, 0]))

u_v = u_v_component(lat_0, lon_0, file_name, i=i_in, j=j_in, pixel_size=pixel_size, center=center,
                    shape=shape, earth_geod=earth_geod, image_geod=image_geod, save_data=save_data)
print('(u, v):', '({0} m/sec, {1} m/sec)'.format(*u_v[:, 0, 0]))

displacements, new_shape = get_displacements(file_name, shape=shape, save_data=save_data)
# np.ndarray.tofile(displacements, 'C:/Users/William/Documents/test')
# test = np.fromfile('C:/Users/William/Documents/test', dtype=np.float32)
# test = test.reshape((2, 1000, 1000))

print('displacements:', *displacements[:, 0, 0], new_shape)

old_lat_long = compute_lat_long(lat_0, lon_0, i=i_in, j=j_in, pixel_size=pixel_size, center=center,
                                shape=new_shape, image_geod=image_geod, save_data=save_data)
print('old_lat, old_long:', *old_lat_long[:, 0, 0])

new_lat_long = compute_lat_long(lat_0, lon_0, displacement_data=file_name, i=i_in, j=j_in, pixel_size=pixel_size,
                                center=center, shape=new_shape, image_geod=image_geod, save_data=save_data)
print('new_lat, new_long:', *new_lat_long[:, 0, 0])

area = get_area(lat_0, lon_0, pixel_size=pixel_size, center=center, shape=new_shape, image_geod=image_geod)
print(area)

end = datetime.utcnow()
print("Execution seconds: ", (end - start).total_seconds())