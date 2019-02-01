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


def _reverse(list_like):
    # Reverses the order of an array. Aka the last element becomes the first, the first becomes the last, etc.
    return tuple(reversed(list_like))


def _pixel_to_pos(i, j, area_definition):
    u_l_pixel = area_definition.pixel_upper_left
    position = u_l_pixel[0] + area_definition.pixel_size_x * i, u_l_pixel[1] - area_definition.pixel_size_y * j
    p = Proj(area_definition.proj_dict, errcheck=True, preserve_units=True)
    tmp_proj_dict = area_definition.proj_dict.copy()
    # Gets position (x, y) in projection space in meters.
    if tmp_proj_dict['units'] != 'm':
        tmp_proj_dict['units'] = 'm'
        position = transform(p, Proj(tmp_proj_dict, errcheck=True, preserve_units=True), *position)
    return position


def get_area(lon_0, lat_0, projection, units, shape, pixel_size, center):
    proj_dict = {'lat_0': lat_0, 'lon_0': lon_0, 'proj': projection, 'units': units}
    p = Proj(proj_dict, errcheck=True, preserve_units=True)
    center = p(*center)
    area_extent = [center[0] - shape[1] * pixel_size / 2, center[1] - shape[0] * pixel_size / 2,
                   center[0] + shape[1] * pixel_size / 2, center[1] + shape[0] * pixel_size / 2]
    return AreaDefinition('3DWinds', '3DWinds', '3DWinds', proj_dict, shape[0], shape[1], area_extent)


def get_displacements(filename, shape=None):
    i_displacements = np.fromfile(filename, dtype=np.float32)[3:][0::2].reshape(shape)
    j_displacements = np.fromfile(filename, dtype=np.float32)[3:][1::2].reshape(shape)
    # Displacements are in pixels.
    return i_displacements, j_displacements


def _calculate_displacement_vector(i, j, delta_i, delta_j, area_definition):
    old_long_lat = _reverse(compute_lat_long(i, j, area_definition))
    new_long_lat = _reverse(compute_lat_long(i + delta_i, j + delta_j, area_definition))
    g = Geod(ellps='WGS84')
    # TODO: IS FORWARD AZIMUTH THE CORRECT ANGLE?
    # 0 is wind vector forward azimuth angle, 1 is wind vector backward azimuth angle, 2 is distance in meters.
    angle, distance = g.inv(*old_long_lat, *new_long_lat)[1:]
    # Returns wind vector backward azimuth rotated 180 degrees and distance.
    return angle + 180, distance


def calculate_velocity(i, j, delta_i, delta_j, area_definition, delta_time=100):
    angle, distance = _calculate_displacement_vector(i, j, delta_i, delta_j, area_definition)
    # meters/second. distance is in meters delta_time is in minutes.
    return distance / (delta_time * 60), angle


def u_v_component(i, j, delta_i, delta_j, area_definition, delta_time=100):
    # When wind vector azimuth is 0 degrees it points Due North (mathematically 90 degrees).
    angle, distance = _calculate_displacement_vector(i, j, delta_i, delta_j, area_definition)
    # meters/second. distance is in meters delta_time is in minutes.
    u = distance / (delta_time * 60) * math.cos((90 - angle) * (math.pi / 180))
    v = distance / (delta_time * 60) * math.sin((90 - angle) * (math.pi / 180))
    return u, v


# TODO: FIX DIFFERENT UNITS
def compute_lat_long(i, j, area_definition):
    proj_dict = area_definition.proj_dict.copy()
    proj_dict['units'] = 'm'
    p = Proj(proj_dict, errcheck=True, preserve_units=True)
    # Returns (lat, long) in degrees.
    return _reverse(p(*_pixel_to_pos(i, j, area_definition), errcheck=True, inverse=True))
