import array
import numpy as np
from pyproj import transform, Proj, Geod
from pyresample.geometry import AreaDefinition
import math


# # https://solarianprogrammer.com/2017/10/25/ppm-image-python-3/
# # PPM header
# width = 256
# height = 128
# maxval = 255
# ppm_header = f'P6 {width} {height} {maxval}\n'
#
# # PPM image data (filled with blue)
# image = array.array('B', [0, 0, 255] * width * height)
#
# # Fill with red the rectangle with origin at (10, 10) and width x height = 50 x 80 pixels
# for y in range(10, 90):
#     for x in range(10, 60):
#         index = 3 * (y * width + x)
#         image[index] = 255  # red channel
#         image[index + 1] = 0  # green channel
#         image[index + 2] = 0  # blue channel
#
# # Save the PPM image as a binary file
# with open('blue_red_example.ppm', 'wb') as f:
#     f.write(bytearray(ppm_header, 'ascii'))
#     image.tofile(f)

# with open('blue_red_example.ppm', 'rb') as f:
#     i = 0
#     data = []
#     for line in f:
#         i += 1
#         set_count = 0
#         if i > 1:
#             sub_data = []
#             for char in line:
#                 data.append(char)
#                 sub_data.append(char)
#                 set_count += 1
#                 print(char, end=' ')
#                 if set_count > 2:
#                     print()
#                     set_count = 0
#         else:
#             print(line)
#         print('-----------------')
# data = np.array(data).reshape([width * height, 3])
# print(data)
# Error for 40 north (math is no longer negligible)?


def get_area(lon_0, lat_0, projection, units, shape, pixel_size, center):
    proj_dict = {'lat_0': lat_0, 'lon_0': lon_0, 'proj': projection, 'units': units}
    p = Proj(proj_dict, preserve_units=True)
    center = p(*center)
    area_extent = [center[0] - shape[1] * pixel_size / 2, center[1] - shape[0] * pixel_size / 2,
                   center[0] + shape[1] * pixel_size / 2, center[1] + shape[0] * pixel_size / 2]
    return AreaDefinition('3DWinds', '3DWinds', '3DWinds', proj_dict, shape[0], shape[1], area_extent)


def get_displacements(filename, shape):
    x_displacements = np.fromfile(filename, dtype=np.float32)[3:][0::2].reshape(shape)
    y_displacements = np.fromfile(filename, dtype=np.float32)[3:][1::2].reshape(shape)
    return x_displacements, y_displacements


def _pixel_to_pos(i, j, area_definition):
    u_l_pixel = area_definition.pixel_upper_left
    return u_l_pixel[0] + area_definition.pixel_size_x * i, u_l_pixel[1] - area_definition.pixel_size_y * j


def _calculate_displacement_vector(i, j, delta_i, delta_j, area_definition):
    old_lat_lon = compute_lat_lon(i, j, area_definition)
    new_lat_lon = compute_lat_lon(i + delta_i, j + delta_j, area_definition)
    # TODO: WHAT SPHERE PROJECTION?
    g = Geod(ellps='WGS84')
    # TODO: IS FORWARD AZIMUTH THE CORRECT ANGLE?
    # 0 is forward azimuth, 1 is backwards azimuth, 2 is distance. Returns forward azimuth and distance.
    return g.inv(*old_lat_lon, *new_lat_lon)[::2]


def calculate_velocity(i, j, delta_i, delta_j, area_definition, delta_time=100):
    angle, distance = _calculate_displacement_vector(i, j, delta_i, delta_j, area_definition)
    return distance / delta_time * 60 / 1000, angle


def u_v_component(i, j, delta_i, delta_j, area_definition, delta_time=100):
    angle, distance = _calculate_displacement_vector(i, j, delta_i, delta_j, area_definition)
    u = distance * math.cos(angle * math.pi / 180) / delta_time * 60 / 1000
    v = distance * math.sin(angle * math.pi / 180) / delta_time * 60 / 1000
    return u, v


def compute_lat_lon(i, j, area_definition):
    p = Proj(area_definition.proj_dict, preserve_units=True)
    return p(*_pixel_to_pos(i, j, area_definition), errcheck=True, inverse=True)
