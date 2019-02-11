from pyproj import Proj, Geod
from pyresample.utils import create_area_def, proj4_str_to_dict
from pyresample.geometry import AreaDefinition
from xarray import DataArray
import numpy as np


"""Find wind info"""


def _extrapolate_i_j(i, j, shape, delta_i=0, delta_j=0):
    """"""
    if np.size(i) != 1 or np.size(j) != 1 or i is None and j is not None or j is None and i is not None:
        raise ValueError('i and j must both be integers or None but were {0} (type: {1}) and {2} (type: {3}) '
                         'respectively'.format(i, type(i), j, type(j)))
    if i is None:
        i = [range(0, shape[1]) for y in range(0, shape[0])]
        j = [[y for x in range(0, shape[1])] for y in range(0, shape[0])]
    # returns (i, j)
    return np.array(i) + delta_i, np.array(j) + delta_j


def _reverse_param(param):
    """"""
    if np.size(param) == 1:
        return param
    if hasattr(param, 'units'):
        return DataArray(list(reversed(param.data.tolist())), attrs={'units': param.units})
    elif isinstance(param, DataArray):
        return list(reversed(param.data.tolist()))
    else:
        return list(reversed(param))


def _get_area_and_displacements(lat_0, lon_0, displacement_data, projection='stere', i=None, j=None,
                                area_extent=None, shape=None, upper_left_extent=None, center=None, pixel_size=None,
                                radius=None, units=None, width=None, height=None, image_geod=None):
    """"""
    # Try to get a shape.
    try:
        area_definition = get_area(lat_0, lon_0, projection=projection, area_extent=area_extent, shape=shape,
                                   upper_left_extent=upper_left_extent, center=center, pixel_size=pixel_size,
                                   radius=radius,
                                   units=units, width=width, height=height, image_geod=image_geod)
        if hasattr(area_definition, 'shape'):
            shape = area_definition.shape
    except ValueError:
        area_definition = None
    delta_i, delta_j, shape = _get_delta(i, j, *get_displacements(displacement_data, shape=shape))
    if not isinstance(area_definition, AreaDefinition):
        area_definition = get_area(lat_0, lon_0, projection=projection, area_extent=area_extent, shape=shape,
                                   upper_left_extent=upper_left_extent, center=center, pixel_size=pixel_size,
                                   radius=radius, units=units, width=width, height=height, image_geod=image_geod)
    if not isinstance(area_definition, AreaDefinition):
        raise ValueError('Not enough information provided to create an area definition')
    return delta_i, delta_j, area_definition


def _to_int(num, error):
    """"""
    if num is None:
        return None
    try:
        if int(num) != num:
            raise TypeError
    except (TypeError, ValueError):
        raise error
    return int(num)


def _get_delta(i, j, displacements, shape):
    """"""
    if displacements is None:
        return 0, 0, shape
    if i is None and j is None:
        return displacements[0], displacements[1], shape
    else:
        return displacements[0, j, i], displacements[1, j, i], shape


def _pixel_to_pos(area_definition, i=None, j=None):
    """"""
    if i is None or j is None:
        i, j = _extrapolate_i_j(i, j, area_definition.shape)
    u_l_pixel = area_definition.pixel_upper_left
    # (x, y) in projection space.
    position = u_l_pixel[0] + area_definition.pixel_size_x * i, u_l_pixel[1] - area_definition.pixel_size_y * j
    return np.array(position)


def _delta_longitude(new_long, old_long):
    """"""
    delta_long = new_long - old_long
    if np.all(abs(delta_long)) > 180.0:
        if np.all(delta_long) > 0.0:
            return delta_long - 360.0
        else:
            return delta_long + 360.0
    return delta_long


def _lat_long_dist(lat, earth_geod):
    """"""
    # Credit: https://gis.stackexchange.com/questions/75528/understanding-terms-in-length-of-degree-formula/75535#75535
    if earth_geod is None:
        earth_geod = 'WGS84'
    geod_info = proj4_str_to_dict(Geod(ellps=earth_geod).initstring)
    a, f = geod_info['a'], geod_info['f']
    e2 = (2 - 1 * f) * f
    lat = np.pi / 180 * lat
    lat_dist = 2 * np.pi * a * (1 - e2) / (1 - e2 * np.sin(lat)**2)**1.5 / 360
    long_dist = 2 * np.pi * a / (1 - e2 * np.sin(lat)**2)**.5 * np.cos(lat) / 360
    return lat_dist, long_dist


def get_area(lat_0, lon_0, projection='stere', area_extent=None, shape=None,
             upper_left_extent=None, center=None, pixel_size=None, radius=None,
             units=None, width=None, height=None, image_geod=None):
    """Computes a projection area from what data the user knows.

    Parameters
    ----------

    Returns
    -------

    """
    # Center is given in (lat, long) order, but create_area_def needs it in (long, lat) order.
    if area_extent is not None:
        area_extent_ll, area_extent_ur = area_extent[0:2], area_extent[2:4]
    else:
        area_extent_ll, area_extent_ur = None, None
    upper_left_extent, center, pixel_size, radius, area_extent_ll, area_extent_ur =\
        np.vectorize(_reverse_param)([upper_left_extent, center, pixel_size, radius, area_extent_ll, area_extent_ur])
    if area_extent is not None:
        area_extent = area_extent_ll + area_extent_ur
    if center is not None and not isinstance(center, DataArray):
        center = DataArray(center, attrs={'units': 'degrees'})
    if image_geod is None:
        image_geod = 'WGS84'
    proj_dict = proj4_str_to_dict('+lat_0={0} +lon_0={1} +proj={2} {3}'.format(lat_0, lon_0, projection,
                                                                               Geod(ellps=image_geod).initstring))
    if proj_dict['f'] == 0:
        proj_dict['b'] = proj_dict['a']
        proj_dict.pop('f')
    return create_area_def('3DWinds', proj_dict, area_extent=area_extent, shape=shape,
                           upper_left_extent=upper_left_extent, resolution=pixel_size,
                           center=center, radius=radius, units=units, width=width, height=height)


def get_displacements(displacement_data, shape=None):
    """Retrieves pixel-displacements from a file or list.

    Parameters
    ----------

    Returns
    -------

    """
    if isinstance(displacement_data, str):
        # Displacement: even index, odd index. Note: (0, 0) is in the top left, i=horizontal and j=vertical.
        i_displacements = np.fromfile(displacement_data, dtype=np.float32)[3:][0::2]
        j_displacements = np.fromfile(displacement_data, dtype=np.float32)[3:][1::2]
    elif displacement_data is not None:
        i_displacements = displacement_data[0]
        j_displacements = displacement_data[1]
    else:
        return None, shape
    if shape is not None:
        displacement_data = (i_displacements.reshape(shape), j_displacements.reshape(shape))
    else:
        try:
            shape = (np.size(i_displacements)**.5, np.size(j_displacements)**.5)
            shape = (_to_int(shape[0], ValueError('')), _to_int(shape[1], ValueError('')))
            displacement_data = (i_displacements.reshape(shape), j_displacements.reshape(shape))
        except ValueError:
            displacement_data = (i_displacements, j_displacements)
            shape = np.size(i_displacements) + np.size(j_displacements)
    return np.array(displacement_data), shape


def calculate_velocity(lat_0, lon_0, displacement_data, projection='stere', i=None, j=None, delta_time=100,
                       area_extent=None, shape=None, upper_left_extent=None, center=None, pixel_size=None,
                       radius=None, units=None, width=None, height=None, image_geod=None,
                       earth_geod=None):
    """Computes speed and angle of the wind given an area and pixel-displacement.

    Parameters
    ----------
    lat_0 : float
        Normal latitude of projection
    lon_0 : float
        Normal longitude of projection
    displacement_data : str or list
        File or list containing displacements: [0, 0, 0, i11, j11, i12, j12, ...] or
        [[i_displacements], [j_displacements]] respectively.
    projection : str
        Name of projection that pixels are describing (stere, laea, merc, etc).
    i : float or None, optional
        Horizontal value of pixel to find lat/long of.
    j : float or None, optional
        Vertical value of pixel to find lat/long of.
    units : str, optional
        Units that provided arguments should be interpreted as. This can be
        one of 'deg', 'degrees', 'rad', 'radians', 'meters', 'metres', and any
        parameter supported by the
        `cs2cs -lu <https://proj4.org/apps/cs2cs.html#cmdoption-cs2cs-lu>`_
        command. Units are determined in the following priority:

        1. units expressed with each variable through a DataArray's attrs attribute.
        2. units passed to ``units``
        3. meters
    area_extent : list, optional
        Area extent as a list (lower_left_x, lower_left_y, upper_right_x, upper_right_y)
    shape : list, optional
        Number of pixels in the y and x direction (height, width). Note that shape
        can be found from the displacement file (in such a case, shape will be square).
    upper_left_extent : list, optional
        Upper left corner of upper left pixel (x, y)
    center : list, optional
        Center of projection (lat, long)
    pixel_size : list or float, optional
        Size of pixels: (dx, dy)
    radius : list or float, optional
        Length from the center to the edges of the projection (dx, dy)
    width : int, optional
        Number of pixels in the x direction
    height : int, optional
        Number of pixels in the y direction
    image_geod : string
        Spheroid of projection

    Returns
    -------
        (speed, angle) : numpy.array
            speed and angle of wind calculated from area and pixel-displacement

    """
    u, v = u_v_component(lat_0, lon_0, displacement_data, projection=projection, i=i, j=j,
                         delta_time=delta_time, area_extent=area_extent, shape=shape,
                         upper_left_extent=upper_left_extent, center=center, pixel_size=pixel_size,
                         radius=radius, units=units, width=width, height=height,
                         image_geod=image_geod, earth_geod=earth_geod)
    # When wind vector azimuth is 0 degrees it points North (npematically 90 degrees) and moves clockwise.
    return np.array(((u**2 + v**2)**.5, ((90 - np.arctan2(v, u) * 180 / np.pi) + 360) % 360))


def u_v_component(lat_0, lon_0, displacement_data, projection='stere', i=None, j=None, delta_time=100,
                  area_extent=None, shape=None, upper_left_extent=None, center=None, pixel_size=None,
                  radius=None, units=None, width=None, height=None, image_geod=None,
                  earth_geod=None):
    """Computes u and v components of the wind given an area and pixel-displacement.

    Parameters
    ----------

    Returns
    -------

    """
    i_error = ValueError('i must be None or an integer but was provided {0} as type {1}'.format(i, type(i)))
    j_error = ValueError('j must be None or an integer but was provided {0} as type {1}'.format(j, type(j)))
    i, j = _to_int(i, i_error), _to_int(j, j_error)
    area_definition = _get_area_and_displacements(lat_0, lon_0, displacement_data, projection=projection, i=i, j=j,
                                                  area_extent=area_extent, shape=shape,
                                                  upper_left_extent=upper_left_extent, center=center,
                                                  pixel_size=pixel_size, radius=radius, units=units, width=width,
                                                  height=height, image_geod=image_geod)[2]
    old_lat, old_long = compute_lat_long(lat_0, lon_0, projection=projection, i=i, j=j, area_extent=area_extent,
                                         shape=area_definition.shape, upper_left_extent=upper_left_extent, center=center,
                                         pixel_size=pixel_size, radius=radius, units=units, width=width, height=height,
                                         image_geod=image_geod)
    new_lat, new_long = compute_lat_long(lat_0, lon_0, projection=projection, i=i, j=j, area_extent=area_extent,
                                         shape=area_definition.shape, upper_left_extent=upper_left_extent, center=center,
                                         pixel_size=pixel_size, radius=radius, units=units, width=width, height=height,
                                         image_geod=image_geod, displacement_data=displacement_data)
    lat_long_distance = _lat_long_dist((new_lat + old_lat) / 2, earth_geod)
    # u = (_delta_longitude(new_long, old_long) *
    #      _lat_long_dist(old_lat, earth_geod)[1] / (delta_time * 60) +
    #      _delta_longitude(new_long, old_long) *
    #      _lat_long_dist(new_lat, earth_geod)[1] / (delta_time * 60)) / 2
    # meters/second. distance is in meters delta_time is in minutes.
    u = _delta_longitude(new_long, old_long) * lat_long_distance[1] / (delta_time * 60)
    v = (new_lat - old_lat) * lat_long_distance[0] / (delta_time * 60)
    return np.array((u, v))


def compute_lat_long(lat_0, lon_0, displacement_data=None, projection='stere', i=None, j=None, area_extent=None,
                     shape=None, upper_left_extent=None, center=None, pixel_size=None, radius=None, units=None,
                     width=None, height=None, image_geod=None):
    """Computes latitude and longitude given an area and pixel-displacement.

    Parameters
    ----------
    lat_0 : float
        Normal latitude of projection
    lon_0 : float
        Normal longitude of projection
    displacement_data : str or list
        File or list containing displacements: [0, 0, 0, i11, j11, i12, j12, ...] or
        [[i_displacements], [j_displacements]] respectively.
    projection : str
        Name of projection that pixels are describing (stere, laea, merc, etc).
    i : float or None, optional
        Horizontal value of pixel to find lat/long of.
    j : float or None, optional
        Vertical value of pixel to find lat/long of.
    units : str, optional
        Units that provided arguments should be interpreted as. This can be
        one of 'deg', 'degrees', 'rad', 'radians', 'meters', 'metres', and any
        parameter supported by the
        `cs2cs -lu <https://proj4.org/apps/cs2cs.html#cmdoption-cs2cs-lu>`_
        command. Units are determined in the following priority:

        1. units expressed with each variable through a DataArray's attrs attribute.
        2. units passed to ``units``
        3. meters
    area_extent : list, optional
        Area extent as a list (lower_left_x, lower_left_y, upper_right_x, upper_right_y)
    shape : list, optional
        Number of pixels in the y and x direction (height, width). Note that shape
        can be found from the displacement file (in such a case, shape will be square).
    upper_left_extent : list, optional
        Upper left corner of upper left pixel (x, y)
    center : list, optional
        Center of projection (lat, long)
    pixel_size : list or float, optional
        Size of pixels: (dx, dy)
    radius : list or float, optional
        Length from the center to the edges of the projection (dx, dy)
    width : int, optional
        Number of pixels in the x direction
    height : int, optional
        Number of pixels in the y direction
    image_geod : string
        Spheroid of projection

    Returns
    -------
        (latitude, longitude) : numpy.array
            latitude and longitude calculated from area and pixel-displacement

    """
    delta_i, delta_j, area_definition = _get_area_and_displacements(lat_0, lon_0, displacement_data,
                                                                    projection=projection, i=i, j=j,
                                                                    area_extent=area_extent, shape=shape,
                                                                    upper_left_extent=upper_left_extent,
                                                                    center=center, pixel_size=pixel_size, radius=radius,
                                                                    units=units, width=width, height=height,
                                                                    image_geod=image_geod)
    # If i and j are None, make them cover the entire image. Also update values with displacements.
    i, j = _extrapolate_i_j(i, j, area_definition.shape, delta_i=delta_i, delta_j=delta_j)
    # Function that handles projection to lat/long transformation.
    p = Proj(area_definition.proj_dict, errcheck=True, preserve_units=True)
    # Returns (lat, long) in degrees.
    return np.array(_reverse_param(p(*_pixel_to_pos(area_definition, i=i, j=j), errcheck=True, inverse=True)))
