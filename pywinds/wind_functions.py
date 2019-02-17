from pyproj import Proj, Geod
from pyresample.utils import create_area_def, proj4_str_to_dict, proj4_dict_to_str
from pyresample.geometry import AreaDefinition
from xarray import DataArray
import ntpath
import numpy as np
import os
import logging


"""Find wind info"""


def _save_data(data, output_filename, input_filename):
    if isinstance(input_filename, str):
        head, tail = ntpath.split(input_filename)
        extenion = tail or ntpath.basename(head)
    else:
        extenion = 'list'
    try:
        os.mkdir(os.path.join(os.getcwd(), extenion + '_output'))
    except OSError:
        pass
    np.ndarray.tofile(np.array(data), os.path.join(os.getcwd(), extenion + '_output', output_filename))


def _extrapolate_j_i(j, i, shape, delta_j=0, delta_i=0):
    """"""
    if np.size(i) != 1 or np.size(j) != 1 or i is None and j is not None or j is None and i is not None:
        raise ValueError('i and j must both be integers or None but were {0} {1} and {2} {3} '
                         'respectively'.format(i, type(i), j, type(j)))
    if i is None:
        j = [[y for x in range(0, shape[1])] for y in range(0, shape[0])]
        i = [range(0, shape[1]) for y in range(0, shape[0])]
    # returns (i, j)
    return np.array(j) + delta_j, np.array(i) + delta_i


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


def _pixel_to_pos(area_definition, j=None, i=None):
    """"""
    if i is None or j is None:
        j, i = _extrapolate_j_i(j, i, area_definition.shape)
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
        earth_geod = Geod(ellps='WGS84')
    elif isinstance(earth_geod, str):
        earth_geod = Geod(ellps=earth_geod)
    else:
        raise ValueError('earth_geod must be a string or Geod type, but instead was {0} as type {1}'.format(
            earth_geod, type(earth_geod)))
    geod_info = proj4_str_to_dict(earth_geod.initstring)
    a, f = geod_info['a'], geod_info['f']
    e2 = (2 - 1 * f) * f
    lat = np.pi / 180 * lat
    lat_dist = 2 * np.pi * a * (1 - e2) / (1 - e2 * np.sin(lat)**2)**1.5 / 360
    long_dist = 2 * np.pi * a / (1 - e2 * np.sin(lat)**2)**.5 * np.cos(lat) / 360
    return lat_dist, long_dist


def _create_area(lat_0, lon_0, projection='stere', area_extent=None, shape=None,
                upper_left_extent=None, center=None, pixel_size=None, radius=None,
                units=None, image_geod=None):
    if not isinstance(projection, str):
        raise ValueError('projection must be a string, but instead was {0} as type {1}'.format(
            projection, type(projection)))
    # Center is given in (lat, long) order, but create_area_def needs it in (long, lat) order.
    if area_extent is not None:
        # The order here is correct since users give input in [ur_y, ur_x, ll_y, ll_x] order.
        area_extent_ur, area_extent_ll = area_extent[0:2], area_extent[2:4]
    else:
        area_extent_ll, area_extent_ur = None, None
    upper_left_extent, center, pixel_size, radius, area_extent_ll, area_extent_ur =\
        np.vectorize(_reverse_param)([upper_left_extent, center, pixel_size, radius, area_extent_ll, area_extent_ur])
    if area_extent is not None:
        # Needs order [ll_x, ll_y, ur_x, ur_y].
        area_extent = area_extent_ll + area_extent_ur
    if center is not None and not isinstance(center, DataArray):
        center = DataArray(center, attrs={'units': 'degrees'})
    if image_geod is None:
        image_geod = Geod(ellps='WGS84')
    elif isinstance(image_geod, str):
        image_geod = Geod(ellps=image_geod)
    else:
        raise ValueError('image_geod must be a string or Geod type, but instead was {0} as type {1}'.format(
            image_geod, type(image_geod)))
    proj_dict = proj4_str_to_dict('+lat_0={0} +lon_0={1} +proj={2} {3}'.format(lat_0, lon_0, projection,
                                                                               image_geod.initstring))
    area = create_area_def('pywinds', proj_dict, area_extent=area_extent, shape=shape,
                           upper_left_extent=upper_left_extent, resolution=pixel_size,
                           center=center, radius=radius, units=units,)
    if isinstance(area_extent, AreaDefinition):
        area.area_extent = tuple(reversed(area.area_extent))
    return area


def _get_displacements(displacement_data=None, j=None, i=None, shape=None, save_data=False):
    """Retrieves pixel-displacements from a file or list.

    Parameters
    ----------

    Returns
    -------
    """
    if isinstance(displacement_data, str):
        # Displacement: even index, odd index. Note: (0, 0) is in the top left, i=horizontal and j=vertical.
        displacements = np.fromfile(displacement_data, dtype=np.float32)[3:]
        j_displacements = displacements[1::2]
        i_displacements = displacements[0::2]
    elif displacement_data is not None:
        if len(np.shape(displacement_data)) == 0 or np.shape(displacement_data)[0] != 2:
            raise ValueError('displacement_data should have shape (2, y, x), but instead has shape {0}'.format(
                np.shape(displacement_data)))
        j_displacements = np.array(displacement_data[1])
        i_displacements = np.array(displacement_data[0])
    else:
        return (0, 0), shape
    if shape is not None:
        j_displacements = j_displacements.reshape(shape)
        i_displacements = i_displacements.reshape(shape)
        j, i = _extrapolate_j_i(j, i, shape)
    else:
        shape = (np.size(i_displacements)**.5, np.size(j_displacements)**.5)
        error = 'Shape was not provided and shape found from file was not comprised of integers: ' \
                '{0} pixels made a shape of {1}'.format(np.size(j_displacements) + np.size(i_displacements),
                                                        tuple([2] + list(shape)))
        shape = (_to_int(shape[0], ValueError(error)), _to_int(shape[1], ValueError(error)))
        j_displacements = j_displacements.reshape(shape)
        i_displacements = i_displacements.reshape(shape)
        j, i = _extrapolate_j_i(j, i, shape)
    if save_data:
        _save_data(j_displacements[j, i], 'j_displacements', displacement_data)
        _save_data(i_displacements[j, i], 'i_displacements', displacement_data)
    return np.array((j_displacements, i_displacements))[:, j, i], shape


def _compute_lat_long(j, i, area_definition, displacement_data, save_data=False, displacements=(0, 0)):
    if not isinstance(area_definition, AreaDefinition):
        raise ValueError('Not enough information provided to create an area definition')
    j_displacement, i_displacement = displacements
    # If i and j are None, make them cover the entire image. Also update values with displacements.
    j, i = _extrapolate_j_i(j, i, area_definition.shape, delta_j=j_displacement, delta_i=i_displacement)
    # Function that handles projection to lat/long transformation.
    p = Proj(area_definition.proj_dict, errcheck=True, preserve_units=True)
    # Returns (lat, long) in degrees.
    lat, long = _reverse_param(p(*_pixel_to_pos(area_definition, j=j, i=i), errcheck=True, inverse=True))
    if save_data == True:
        if displacement_data is None:
            raise ValueError('Cannot save old latitudes/longitudes to a file')
        else:
            _save_data(lat, 'new_latitude', displacement_data)
            _save_data(long, 'new_longitude', displacement_data)
    return np.array((lat, long))


def get_displacements_and_area(lat_0=None, lon_0=None, displacement_data=None, projection='stere', j=None, i=None,
                                area_extent=None, shape=None, upper_left_extent=None, center=None, pixel_size=None,
                                radius=None, units=None, image_geod=None, save_data=False):
    """"""
    # Try to get a shape.
    area_definition = None
    if lat_0 is not None or lon_0 is not None:
        try:
            area_definition = _create_area(lat_0, lon_0, projection=projection, area_extent=area_extent, shape=shape,
                                       upper_left_extent=upper_left_extent, center=center, pixel_size=pixel_size,
                                       radius=radius, units=units, image_geod=image_geod)
            shape = (area_definition.height, area_definition.width)
        except ValueError:
            pass
    displacements, shape = _get_displacements(displacement_data, shape=shape, j=j, i=i, save_data=save_data)
    if not isinstance(area_definition, AreaDefinition) and (lat_0 is not None or lon_0 is not None):
        area_definition = _create_area(lat_0, lon_0, projection=projection, area_extent=area_extent, shape=shape,
                                   upper_left_extent=upper_left_extent, center=center, pixel_size=pixel_size,
                                   radius=radius, units=units, image_geod=image_geod)
    return np.array((displacements, area_definition))


def calculate_velocity(lat_0, lon_0, displacement_data=None, projection='stere', j=None, i=None, delta_time=100,
                       area_extent=None, shape=None, upper_left_extent=None, center=None, pixel_size=None,
                       radius=None, units=None, image_geod=None,
                       earth_geod=None, save_data=False):
    """Computes the speed and angle of the wind given an area and pixel-displacement.

    Parameters
    ----------
    lat_0 : float
        Normal latitude of projection
    lon_0 : float
        Normal longitude of projection
    displacement_data : str or list
        File or list containing displacements: [0, 0, 0, i11, j11, i12, j12, ...] or
        [[j_displacements], [i_displacements]] respectively.
    projection : str
        Name of projection that pixels are describing (stere, laea, merc, etc).
    j : float or None, optional
        Vertical value of pixel to find lat/long of.
    i : float or None, optional
        Horizontal value of pixel to find lat/long of.
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
        Area extent as a list (upper_right_y, upper_right_x, lower_left_y, lower_left_x)
    shape : list, optional
        Number of pixels in the y and x direction (height, width). Note that shape
        can be found from the displacement file (in such a case, shape will be square)
    upper_left_extent : list, optional
        Upper left corner of upper left pixel (y, x)
    center : list, optional
        Center of projection (lat, long)
    pixel_size : list or float, optional
        Size of pixels: (dy, dx)
    radius : list or float, optional
        Length from the center to the edges of the projection (dy, dx)
    image_geod : string or Geod
        Spheroid of projection
    earth_geod : string or Geod
        Spheroid of Earth
    save_data : bool
        When True, saves lat to output_data/speed and long to output_data/angle

    Returns
    -------
        (speed, angle) : numpy.array or list
            speed and angle (measured clockwise from north) of the wind calculated from area and pixel-displacement
    """
    v, u = v_u_component(lat_0, lon_0, displacement_data=displacement_data, projection=projection, j=j, i=i,
                         delta_time=delta_time, area_extent=area_extent, shape=shape,
                         upper_left_extent=upper_left_extent, center=center, pixel_size=pixel_size,
                         radius=radius, units=units,
                         image_geod=image_geod, earth_geod=earth_geod)
    speed, angle = (u**2 + v**2)**.5, ((90 - np.arctan2(v, u) * 180 / np.pi) + 360) % 360
    if save_data == True:
        _save_data(speed, 'speed', displacement_data)
        _save_data(angle, 'angle', displacement_data)
    # When wind vector azimuth is 0 degrees it points North (mathematically 90 degrees) and moves clockwise.
    return np.array((speed, angle))


def v_u_component(lat_0, lon_0, displacement_data=None, projection='stere', j=None, i=None, delta_time=100,
                  area_extent=None, shape=None, upper_left_extent=None, center=None, pixel_size=None,
                  radius=None, units=None, image_geod=None,
                  earth_geod=None, save_data=False):
    """Computes the v and u components of the wind given an area and pixel-displacement.

    Parameters
    ----------
    lat_0 : float
        Normal latitude of projection
    lon_0 : float
        Normal longitude of projection
    displacement_data : str or list
        File or list containing displacements: [0, 0, 0, i11, j11, i12, j12, ...] or
        [[j_displacements], [i_displacements]] respectively.
    projection : str
        Name of projection that pixels are describing (stere, laea, merc, etc).
    j : float or None, optional
        Vertical value of pixel to find lat/long of.
    i : float or None, optional
        Horizontal value of pixel to find lat/long of.
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
        Area extent as a list (upper_right_y, upper_right_x, lower_left_y, lower_left_x)
    shape : list, optional
        Number of pixels in the y and x direction (height, width). Note that shape
        can be found from the displacement file (in such a case, shape will be square)
    upper_left_extent : list, optional
        Upper left corner of upper left pixel (y, x)
    center : list, optional
        Center of projection (lat, long)
    pixel_size : list or float, optional
        Size of pixels: (dy, dx)
    radius : list or float, optional
        Length from the center to the edges of the projection (dy, dx)
    image_geod : string or Geod
        Spheroid of projection
    earth_geod : string or Geod
        Spheroid of Earth
    save_data : bool
        When True, saves lat to output_data/v and long to output_data/u

    Returns
    -------
        (v, u) : numpy.array or list
            v and u components of wind calculated from area and pixel-displacement
    """
    displacements, area_definition = get_displacements_and_area(lat_0, lon_0, displacement_data, projection=projection, j=j, i=i,
                                                  area_extent=area_extent, shape=shape,
                                                  upper_left_extent=upper_left_extent, center=center,
                                                  pixel_size=pixel_size, radius=radius, units=units,
                                                  image_geod=image_geod)
    if not isinstance(area_definition, AreaDefinition):
        raise ValueError('Not enough information provided to create an area definition')
    old_lat, old_long = _compute_lat_long(j, i, area_definition, displacement_data)
    new_lat, new_long = _compute_lat_long(j, i, area_definition, displacement_data, displacements=displacements)
    lat_long_distance = _lat_long_dist((new_lat + old_lat) / 2, earth_geod)
    # u = (_delta_longitude(new_long, old_long) *
    #      _lat_long_dist(old_lat, earth_geod)[1] / (delta_time * 60) +
    #      _delta_longitude(new_long, old_long) *
    #      _lat_long_dist(new_lat, earth_geod)[1] / (delta_time * 60)) / 2
    # meters/second. distance is in meters delta_time is in minutes.
    v = (new_lat - old_lat) * lat_long_distance[0] / (delta_time * 60)
    u = _delta_longitude(new_long, old_long) * lat_long_distance[1] / (delta_time * 60)
    if save_data == True:
        _save_data(u, 'u', displacement_data)
        _save_data(v, 'v', displacement_data)
    return np.array((v, u))


def compute_lat_long(lat_0, lon_0, displacement_data=None, projection='stere', j=None, i=None, area_extent=None,
                     shape=None, upper_left_extent=None, center=None, pixel_size=None, radius=None, units=None,
                     image_geod=None, save_data=False):
    """Computes the latitude and longitude given an area and (j, i) values.

    Parameters
    ----------
    lat_0 : float
        Normal latitude of projection
    lon_0 : float
        Normal longitude of projection
    displacement_data : str or list
        File or list containing displacements: [0, 0, 0, i11, j11, i12, j12, ...] or
        [[j_displacements], [i_displacements]] respectively. If provided, finds the
        latitude/longitude at (j,i) + displacements.
    projection : str
        Name of projection that pixels are describing (stere, laea, merc, etc).
    j : float or None, optional
        Vertical value of pixel location (row)
    i : float or None, optional
        Horizontal value of pixel location (column)
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
        Area extent as a list (upper_right_y, upper_right_x, lower_left_y, lower_left_x)
    shape : list, optional
        Number of pixels in the y and x direction (height, width). Note that shape
        can be found from the displacement file (in such a case, shape will be square)
        or the area provided.
    upper_left_extent : list, optional
        Upper left corner of upper left pixel (y, x)
    center : list, optional
        Center of projection (lat, long)
    pixel_size : list or float, optional
        Size of pixels: (dy, dx)
    radius : list or float, optional
        Length from the center to the edges of the projection (dy, dx)
    image_geod : string or Geod
        Spheroid of projection
    save_data : bool
        When True, saves lat to output_data/latitude and long to output_data/longitude

    Returns
    -------
        (latitude, longitude) : numpy.array or list
            latitude and longitude calculated from area and pixel-displacement

    Notes
    -----
    * center will always be interpreted as degrees unless units are passed directly with center
    * The list returned is in row-column form. lat[j][i] is up/down j pixels and left/right i pixels
    """
    if not isinstance(lat_0, (int, float)) or not isinstance(lon_0, (int, float)):
        raise ValueError('lat_0 and lon_0 must be ints or floats, but instead were ' +
                         '{0} as type {1} and {2} as type {3} respectively'.format(
                             lat_0, type(lat_0), lon_0, type(lon_0)))
    displacements, area_definition = get_displacements_and_area(lat_0, lon_0, displacement_data,
                                                                    projection=projection, j=j, i=i,
                                                                    area_extent=area_extent, shape=shape,
                                                                    upper_left_extent=upper_left_extent,
                                                                    center=center, pixel_size=pixel_size,
                                                                    radius=radius, units=units, 
                                                                    image_geod=image_geod)
    return _compute_lat_long(j, i, area_definition, displacement_data, save_data=save_data, displacements=displacements)
