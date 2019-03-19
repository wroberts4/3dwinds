import sys
from datetime import datetime
from pywinds.wind_functions import area, wind_info, velocity, displacements, lat_long, vu
import xarray
import numpy as np
import os


start = datetime.utcnow()
file_name = 'in.flo'
lat_ts = 60
lat_0 = 90
lon_0 = 0
i_in = None
j_in = None
pixel_size = 4000
center = (90, 0)
shape = (1000, 1000)
earth_spheroid = 'WGS84'
projection_spheroid = 'WGS84'
no_save = False
area_extent = tuple(reversed((2000000.0, 5429327.9172, -2000000.0, 1429327.9172)))

# speed = xarray.DataArray([5, 5], name='speed')
# angle = xarray.DataArray([10, 10], name='angle')
# velocity = xarray.Dataset({'speed': speed, 'angle': angle})
# velocity.to_netcdf('C:/Users/William/Documents/pywinds/test.netcdf4', group='velocity', mode='w', format='NETCDF4',
#                    encoding={var: {'dtype': float} for var in dict(velocity.data_vars).keys()})
# lat = xarray.DataArray([50, 50], name='lat')
# long = xarray.DataArray([100, 100], name='long')
# lat_long = xarray.Dataset({'lat': lat, 'long': long})
# lat_long.to_netcdf('C:/Users/William/Documents/pywinds/test.netcdf4', mode='a', group='lat_long', format='NETCDF4')
# print(xarray.open_dataset('C:/Users/William/Documents/pywinds/test.netcdf4'))
#
winds = wind_info(lat_ts, lat_0, lon_0, 100, displacement_data=file_name, center=center,
                  pixel_size=pixel_size, i=0, j=0)
# print(winds[500, 500, :])
#
# output_velocity = velocity(lat_ts, lat_0, lon_0, 100, displacement_data='in.flo', i=i_in, j=j_in, pixel_size=pixel_size,
#                            center=center, earth_spheroid=earth_spheroid, projection_spheroid=projection_spheroid, no_save=no_save)
# print('speed:', '{0} m/sec, {1}°'.format(*output_velocity[:, 0, 0]))
#
# output_vu = vu(lat_ts, lat_0, lon_0, 100, i=i_in, j=j_in, pixel_size=pixel_size, center=center,
#                displacement_data=file_name, shape=shape, earth_spheroid=earth_spheroid, projection_spheroid=projection_spheroid, no_save=no_save)
# print('(v, u):', '({0} m/sec, {1} m/sec)'.format(*output_vu[:, 0, 0]))
#
# area_def = area(lat_ts, lat_0, lon_0, displacement_data=file_name, pixel_size=pixel_size)
# print(xarray.open_dataset('./in.flo_output/wind_info.nc'))
# print(area_def)
#
# displacement = displacements(displacement_data=file_name, no_save=no_save)
# print(xarray.open_dataset('./in.flo_output/wind_info.nc'))
# print('displacements:', *displacement[:, 0, 0])
#
# new_lat_long = lat_long(lat_ts, lat_0, lon_0, i=i_in, j=j_in, pixel_size=pixel_size, center=center,
#                         shape=(1000,1000), projection_spheroid=projection_spheroid, no_save=True)
# print('new_lat, new_long:', *new_lat_long[:, 999, 0])
#
# old_lat_long = lat_long(lat_ts, lat_0, lon_0, displacement_data=file_name, i=0, j=0, pixel_size=pixel_size,
#                                 center=center, shape=(1000,1000), projection_spheroid=projection_spheroid, no_save=no_save)
# print('old_lat, old_long:', *old_lat_long[:, 999, 0])
#
# hdf5 = h5py.File('in.flo_output/wind_info.hdf5', 'r')
# for group in hdf5.keys():
#     if isinstance(hdf5[group], h5py.Group):
#         for key in hdf5[group].keys():
#             print(group, key, np.array(hdf5[group][key]), [attr + ': ' +  hdf5[group][key].attrs[attr]
#                                                           for attr in hdf5[group][key].attrs])
#     else:
#         print(group, np.array(hdf5[group]), [attr + ': ' + hdf5[group].attrs[attr] for attr in hdf5[group].attrs])
# hdf5.close()

end = datetime.utcnow()
print("Execution seconds: ", (end - start).total_seconds())
