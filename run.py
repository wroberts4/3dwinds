from pywinds.main import calculate_velocity, u_v_component, compute_lat_long, get_displacements, get_area
from xarray import DataArray
import numpy as np


# header = [0, 0, 0]
# first_row = np.ones(6)*2
# second_row = np.ones(6)*3
# third_row = np.ones(6)*4
# np.ndarray.tofile(np.array(header + list(first_row) + list(second_row) + list(third_row), dtype=np.float32),
#                   '/Users/wroberts/Documents/pywinds/test')
# displacements, new_shape = get_displacements('/Users/wroberts/Documents/pywinds/test')
# print(displacements)

file_name = 'C:/Users/William/Documents/pywinds/airs1.flo'
lat_0 = 60
lon_0 = 0
i_in = None
j_in = None
i_out = 100
j_out = 0
pixel_size = 4000
center = (90, 0)
shape = None
# TODO: FIGURE OUT WHY SLICING AND I,J ARE NOT THE SAME
# velocity = calculate_velocity(lat_0, lon_0, file_name, i=i_in, j=j_in, pixel_size=pixel_size,
#                               center=center, shape=shape)
# print('speed:', '{0} m/sec, {1}°'.format(*velocity[:, j_out, i_out]))
#
# u_v = u_v_component(lat_0, lon_0, file_name, i=i_in, j=j_in, pixel_size=pixel_size, center=center, shape=shape)
# print('(u, v):', '({0} m/sec, {1} m/sec)'.format(*u_v[:, j_out, i_out]))
# print(u_v[:, :3, :3])
print(u_v_component(lat_0, lon_0, file_name, i=i_out, j=j_out, pixel_size=pixel_size, center=center, shape=shape))
#
# displacements, new_shape = get_displacements(file_name, shape=shape)
# print('displacements:', *displacements[:, 0:3, 0:3], new_shape)
#
# old_lat_long = compute_lat_long(lat_0, lon_0, i=i_in, j=j_in, pixel_size=pixel_size, center=center, shape=new_shape)
# print('old_lat, old_long:', *old_lat_long[:, j_out, i_out])
#
# new_lat_long = compute_lat_long(lat_0, lon_0, displacement_data=file_name, i=i_in, j=j_in,
#                                 pixel_size=pixel_size, center=center, shape=new_shape)
# print('new_lat, new_long:', *new_lat_long[:, j_out, i_out])
#
# area = get_area(lat_0, lon_0, pixel_size=pixel_size, center=center, shape=new_shape)
# print(area)
