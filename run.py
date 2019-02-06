from main import calculate_velocity, u_v_component, compute_lat_long, get_displacements, get_area
from xarray import DataArray
import numpy as np
speed, angle = calculate_velocity('C:/Users/William/Documents/3dwinds/airs1.flo', 60, 0,
                                  i=0, j=0, pixel_size=4000, center=(90, 0))
print('speed:', '{0} m/sec, {1}°'.format(speed, angle))

u, v = u_v_component('C:/Users/William/Documents/3dwinds/airs1.flo', 60, 0, i=0, j=0, pixel_size=4000, center=(90, 0))
print('(u, v):', '({0} m/sec, {1} m/sec)'.format(u, v))

lat, long = compute_lat_long(60, 0, i=0, j=0, pixel_size=4000, center=(90, 0), shape=(1000, 1000))
print('lat, long:', lat, long)

displacements, shape = get_displacements('C:/Users/William/Documents/3dwinds/airs1.flo')

print('displacements:', np.size(displacements[0]), shape)

area = get_area(60, 0, pixel_size=4000, center=(90, 0), shape=(1000, 1000))

print(area)
