from pyproj import transform, Proj, Geod
from pyresample.geometry import AreaDefinition
import numpy as np
import math


def _pixel_to_pos(i, j, area_definition):
    u_l_pixel = area_definition.pixel_upper_left
    # (x, y) in projection space.
    position = u_l_pixel[0] + area_definition.pixel_size_x * i, u_l_pixel[1] - area_definition.pixel_size_y * j
    p = Proj(area_definition.proj_dict, errcheck=True, preserve_units=True)
    tmp_proj_dict = area_definition.proj_dict.copy()
    # Get position in meters.
    if tmp_proj_dict['units'] != 'm':
        tmp_proj_dict['units'] = 'm'
        position = transform(p, Proj(tmp_proj_dict, errcheck=True, preserve_units=True), *position)
    return position


def _delta_longitude(long1, long2):
    delta_long = long1 - long2
    if abs(delta_long) > 180.0:
        if delta_long > 0.0:
            return delta_long - 360.0
        else:
            return delta_long + 360.0
    return delta_long


def _lat_long_dist(lat, **kwargs):
    # Credit: https://gis.stackexchange.com/questions/75528/understanding-terms-in-length-of-degree-formula/75535#75535
    g = Geod(ellps='WGS84')
    # Only allow values that are not None in kwargs:
    for key, val in kwargs.items():
        if val is not None:
            g = Geod(**{key: val for key, val in kwargs.items() if val is not None})
            break
    lat = math.pi / 180 * lat
    e2 = (2 - 1 * g.f) * g.f
    lat_dist = 2 * math.pi * g.a * (1 - e2) / (1 - e2 * math.sin(lat) ** 2) ** 1.5 / 360
    long_dist = 2 * math.pi * g.a / (1 - e2 * math.sin(lat) ** 2) ** .5 * math.cos(lat) / 360
    return lat_dist, long_dist


def get_area(projection, lat_lon_0, shape, pixel_size, center=(0, 90), units='m'):
    proj_dict = {'lat_0': lat_lon_0[0], 'lon_0': lat_lon_0[1], 'proj': projection, 'units': units}
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


def calculate_velocity(i, j, delta_i, delta_j, area_definition, delta_time=100):
    u, v = u_v_component(i, j, delta_i, delta_j, area_definition, delta_time=delta_time)
    # When wind vector azimuth is 0 degrees it points North (mathematically 90 degrees) and moves clockwise.
    return (u**2 + v**2)**.5, ((90 - math.atan2(v, u) * 180 / math.pi) + 360) % 360


def u_v_component(i, j, delta_i, delta_j, area_definition, delta_time=100,
                  ellps=None, a=None, b=None, rf=None, f=None, **kwargs):
    old_lat, old_long = compute_lat_long(i, j, area_definition)
    new_lat, new_long = compute_lat_long(i + delta_i, j + delta_j, area_definition)
    lat_long_distance = _lat_long_dist((new_lat + old_lat) / 2, ellps=ellps, a=a, b=b, rf=rf, f=f, **kwargs)
    # u = (_delta_longitude(new_long, old_long) *
    #      _lat_long_dist(old_lat, ellps=ellps, a=a, b=b, rf=rf, f=f, **kwargs)[1] / (delta_time * 60) +
    #      _delta_longitude(new_long, old_long) *
    #      _lat_long_dist(new_lat, ellps=ellps, a=a, b=b, rf=rf, f=f, **kwargs)[1] / (delta_time * 60)) / 2
    # meters/second. distance is in meters delta_time is in minutes.
    u = _delta_longitude(new_long, old_long) * lat_long_distance[1] / (delta_time * 60)
    v = (new_lat - old_lat) * lat_long_distance[0] / (delta_time * 60)
    return u, v


def compute_lat_long(i, j, area_definition):
    proj_dict = area_definition.proj_dict.copy()
    proj_dict['units'] = 'm'
    p = Proj(proj_dict, errcheck=True, preserve_units=True)
    # Returns (lat, long) in degrees.
    return tuple(reversed(p(*_pixel_to_pos(i, j, area_definition), errcheck=True, inverse=True)))
