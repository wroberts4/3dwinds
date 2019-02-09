from pywinds.main import calculate_velocity, u_v_component, compute_lat_long, get_displacements, get_area
from xarray import DataArray
from datetime import datetime
import numpy as np
from pyproj import Geod


start = datetime.utcnow()
file_name = 'C:/Users/William/Documents/pywinds/pywinds/test/test_files/test_data_one.flo'
lat_0 = 60
lon_0 = 0
i_in = None
j_in = None
pixel_size = 400000
center = (90, 0)
shape = None
earth_geod = Geod(ellps='WGS84')
velocity = calculate_velocity(lat_0, lon_0, file_name, i=i_in, j=j_in, pixel_size=pixel_size,
                              center=center, shape=shape, earth_geod=earth_geod)
print('speed:', '{0} m/sec, {1}°'.format(*velocity[:, 0, 0]))

u_v = u_v_component(lat_0, lon_0, file_name, i=i_in, j=j_in, pixel_size=pixel_size,
                    center=center,shape=shape, earth_geod=earth_geod)
print('(u, v):', '({0} m/sec, {1} m/sec)'.format(*u_v[:, 0, 0]))

displacements, new_shape = get_displacements(file_name, shape=shape)
print('displacements:', *displacements[:, 0, 0], new_shape)

old_lat_long = compute_lat_long(lat_0, lon_0, i=i_in, j=j_in, pixel_size=pixel_size, center=center, shape=new_shape)
print('old_lat, old_long:', *old_lat_long[:, 0, 0])

new_lat_long = compute_lat_long(lat_0, lon_0, displacement_data=file_name, i=i_in, j=j_in,
                                pixel_size=pixel_size, center=center, shape=new_shape)
print('new_lat, new_long:', *new_lat_long[:, 0, 0])

area = get_area(lat_0, lon_0, pixel_size=pixel_size, center=center, shape=new_shape)
print(area)

end = datetime.utcnow()
print("Execution seconds: ", (end - start).total_seconds())