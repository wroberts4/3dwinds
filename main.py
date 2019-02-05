from pyproj import transform, Proj, Geod
from pyresample.geometry import AreaDefinition
from pyresample.utils import proj4_str_to_dict
import numpy as np


def _extrapolate_i_j(i, j, shape, delta_i=0, delta_j=0):
    if np.size(i) != 1 or np.size(j) != 1 or i is None and j is not None or j is None and i is not None:
        raise ValueError('i and j must both be integers or None but were {0} (type: {1}) and {2} (type: {3}) '
                         'respectively'.format(i, type(i), j, type(j)))
    if i is None:
        i = [range(0, shape[1]) for y in range(0, shape[0])]
        j = [[y for x in range(0, shape[1])] for y in range(0, shape[0])]
    # returns (i, j)
    return np.array(i) + delta_i, np.array(j) + delta_j


def _to_int(num, error):
    if num is None:
        return None
    try:
        if int(num) != num:
            raise TypeError
    except TypeError:
        raise error
    return int(num)


def _get_delta(i, j, displacements, shape):
    if i is None and j is None:
        return displacements[0], displacements[1], shape
    else:
        return displacements[0][i][j], displacements[1][i][j], shape


def _pixel_to_pos(area_definition, i=None, j=None):
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


def _delta_longitude(new_long, old_long):
    delta_long = new_long - old_long
    if np.all(abs(delta_long)) > 180.0:
        if np.all(delta_long) > 0.0:
            return delta_long - 360.0
        else:
            return delta_long + 360.0
    return delta_long


def _lat_long_dist(lat, g):
    # Credit: https://gis.stackexchange.com/questions/75528/understanding-terms-in-length-of-degree-formula/75535#75535
    lat = np.pi / 180 * lat
    lat_dist = 2 * np.pi * g.a * (1 - g.es) / (1 - g.es * np.sin(lat)**2)**1.5 / 360
    long_dist = 2 * np.pi * g.a / (1 - g.es * np.sin(lat)**2)**.5 * np.cos(lat) / 360
    return lat_dist, long_dist


def _compute_lat_long(projection='stere', i=None, j=None, shape=None, pixel_size=None, lat_0=None, lon_0=None,
                      image_geod=Geod(ellps='WGS84'), units='m', center=None, delta_i=0, delta_j=0):
    i, j = _extrapolate_i_j(i, j, shape, delta_i, delta_j)
    area_definition = get_area(projection, (lat_0, lon_0), shape, pixel_size, center=center, units=units,
                               geod=image_geod)
    proj_dict = area_definition.proj_dict.copy()
    proj_dict['units'] = 'm'
    p = Proj(proj_dict, errcheck=True, preserve_units=True)
    # Returns (lat, long) in degrees.
    return tuple(reversed(p(*_pixel_to_pos(area_definition, i=i, j=j), errcheck=True,
                            inverse=True)))


def get_area(projection, lat_long_0, shape, pixel_size, center=None, units='m', geod=None):
    proj_string = '+lat_0=' + str(lat_long_0[0]) + ' +lon_0=' + str(lat_long_0[1]) +\
                  ' +proj=' + projection + ' +units=' + units + ' ' + geod.initstring
    proj_dict = proj4_str_to_dict(proj_string)
    p = Proj(proj_dict, errcheck=True, preserve_units=True)
    center = p(*tuple(reversed(center)))
    area_extent = [center[0] - shape[1] * pixel_size / 2, center[1] - shape[0] * pixel_size / 2,
                   center[0] + shape[1] * pixel_size / 2, center[1] + shape[0] * pixel_size / 2]
    return AreaDefinition('3DWinds', '3DWinds', '3DWinds', proj_dict, shape[0], shape[1], area_extent)


def get_displacements(displacement_data, shape=None):
    if isinstance(displacement_data, str):
        # Displacement: even index, odd index. Note: (0, 0) is in the top left, i=horizontal and j=vertical.
        i_displacements = np.fromfile(displacement_data, dtype=np.float32)[3:][0::2]
        j_displacements = np.fromfile(displacement_data, dtype=np.float32)[3:][1::2]
        if shape is not None:
            displacement_data = (i_displacements.reshape(shape), j_displacements.reshape(shape))
        else:
            shape = (np.size(i_displacements)**.5, np.size(j_displacements)**.5)
            error = ValueError('shape was not provided, and an integer shape could not be found from '
                               '{0}: '.format(displacement_data, shape))
            shape = (_to_int(shape[0], error), _to_int(shape[1], error))
            displacement_data = (i_displacements.reshape(shape), j_displacements.reshape(shape))
    return displacement_data, shape


def calculate_velocity(displacement_data, projection='stere', i=None, j=None, delta_time=100, shape=None,
                       pixel_size=None,
                       lat_0=None, lon_0=None, image_geod=Geod(ellps='WGS84'), earth_geod=Geod(ellps='WGS84'),
                       units='m', center=None):
    u, v = u_v_component(displacement_data, projection=projection, i=i, j=j, delta_time=delta_time, shape=shape,
                         image_geod=image_geod, earth_geod=earth_geod, pixel_size=pixel_size, lat_0=lat_0,
                         lon_0=lon_0, units=units, center=center)
    # When wind vector azimuth is 0 degrees it points North (npematically 90 degrees) and moves clockwise.
    return (u**2 + v**2)**.5, ((90 - np.arctan2(v, u) * 180 / np.pi) + 360) % 360


def u_v_component(displacement_data, projection='stere', i=None, j=None, delta_time=100, shape=None,
                  pixel_size=None, lat_0=None, lon_0=None, center=None, image_geod=Geod(ellps='WGS84'),
                  earth_geod=Geod(ellps='WGS84'), units='m'):
    i_error = ValueError('i must be None or an integer but was provided {0} as type {1}'.format(i, type(i)))
    j_error = ValueError('j must be None or an integer but was provided {0} as type {1}'.format(j, type(j)))
    i, j = _to_int(i, i_error), _to_int(j, j_error)
    delta_i, delta_j, shape = _get_delta(i, j, *get_displacements(displacement_data, shape=shape))
    old_lat, old_long = _compute_lat_long(projection=projection, i=i, j=j, shape=shape, pixel_size=pixel_size,
                                          lat_0=lat_0, lon_0=lon_0, image_geod=image_geod, units=units, center=center)
    new_lat, new_long = _compute_lat_long(projection=projection, i=i, j=j, shape=shape, pixel_size=pixel_size,
                                          lat_0=lat_0, lon_0=lon_0, image_geod=image_geod, units=units, center=center,
                                          delta_i=delta_i, delta_j=delta_j)
    lat_long_distance = _lat_long_dist((new_lat + old_lat) / 2, earth_geod)
    # u = (_delta_longitude(new_long, old_long) *
    #      _lat_long_dist(old_lat, ellps=ellps, a=a, b=b, rf=rf, f=f, **kwargs)[1] / (delta_time * 60) +
    #      _delta_longitude(new_long, old_long) *
    #      _lat_long_dist(new_lat, ellps=ellps, a=a, b=b, rf=rf, f=f, **kwargs)[1] / (delta_time * 60)) / 2
    # meters/second. distance is in meters delta_time is in minutes.
    u = _delta_longitude(new_long, old_long) * lat_long_distance[1] / (delta_time * 60)
    v = (new_lat - old_lat) * lat_long_distance[0] / (delta_time * 60)
    return u, v


def compute_lat_long(projection='stere', i=None, j=None, shape=None, pixel_size=None, lat_0=None,
                     lon_0=None, image_geod=Geod(ellps='WGS84'), units='m', center=None):
    return _compute_lat_long(projection=projection, i=i, j=j, shape=shape, pixel_size=pixel_size, lat_0=lat_0,
                             lon_0=lon_0, image_geod=image_geod, units=units, center=center)
