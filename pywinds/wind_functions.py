from pyproj import Proj, Geod
from pyresample.utils import proj4_str_to_dict
from pyresample import create_area_def
from pyresample.geometry import AreaDefinition
from xarray import DataArray
import ntpath
import numpy as np
import os


"""Find wind info"""


def _no_save(data, output_filename, input_filename):
    """Saves data to a file named after the displacement_data appended with "_output"."""
    if isinstance(input_filename, str):
        head, tail = ntpath.split(input_filename)
        extenion = tail or ntpath.basename(head)
    else:
        extenion = 'list'
    try:
        os.mkdir(os.path.join(os.getcwd(), extenion + '_output'))
    except OSError:
        pass
    if np.size(data) == 1:
        data = np.ravel(data)
    np.ndarray.tofile(data, os.path.join(os.getcwd(), extenion + '_output', output_filename + '.out'),
                      format='%.2f')
    np.savetxt(os.path.join(os.getcwd(), extenion + '_output', output_filename + '.txt'), data, fmt='%.2f')


def _extrapolate_j_i(j, i, shape):
    """Extrapolates j and i to be the entire image if they are not provided."""
    if np.size(i) != 1 or np.size(j) != 1 or i is None and j is not None or j is None and i is not None:
        raise ValueError('i and j must both be integers or None but were {0} {1} and {2} {3} '
                         'respectively'.format(i, type(i), j, type(j)))
    if i is None:
        j = [x for x in range(0, shape[1]) for y in range(0, shape[0])]
        i = [y for x in range(0, shape[1]) for y in range(0, shape[0])]
    else:
        if j >= shape[0]:
            raise IndexError('index {0} is out of bounds for vertical axis with size {1}'.format(j, shape[0]))
        if i >= shape[1]:
            raise IndexError('index {0} is out of bounds for horizontal axis with size {1}'.format(i, shape[1]))
        i = _to_int(i, ValueError('i must be a positive integer'))
        j = _to_int(j, ValueError('j must be a positive integer'))
        if i < 0:
            raise ValueError('i must be a positive integer')
        if j < 0:
            raise ValueError('j must be a positive integer')
    # returns (i, j)
    return np.array(j), np.array(i)


def _reverse_param(param):
    """Reverses the order of parameters (y/x-form is given, but most packages need x/y-form."""
    if np.size(param) == 1:
        return param
    if hasattr(param, 'units'):
        return DataArray(list(reversed(param.data.tolist())), attrs={'units': param.units})
    elif isinstance(param, DataArray):
        return list(reversed(param.data.tolist()))
    else:
        return list(reversed(param))


def _to_int(num, error):
    """Converts objects to integers."""
    if num is None:
        return None
    try:
        if int(num) != num:
            raise TypeError
    except (TypeError, ValueError):
        raise error
    return int(num)


def _pixel_to_pos(area_definition, j, i):
    """Converts (j, i) pixels to a position on the Earth in projection space."""
    u_l_pixel = area_definition.pixel_upper_left
    # (x, y) in projection space.
    position = u_l_pixel[0] + area_definition.pixel_size_x * i, u_l_pixel[1] - area_definition.pixel_size_y * j
    return np.array(position)


def _delta_longitude(new_long, old_long):
    """Calculates the change in longitude on the Earth."""
    delta_long = new_long - old_long
    if np.all(abs(delta_long)) > 180.0:
        if np.all(delta_long) > 0.0:
            return delta_long - 360.0
        else:
            return delta_long + 360.0
    return delta_long


def _lat_long_dist(lat, earth_geod):
    """Calculates the distance between latitudes and longitudes given a latitude."""
    if earth_geod is None:
        earth_geod = Geod(ellps='WGS84')
    elif isinstance(earth_geod, str):
        earth_geod = Geod(ellps=earth_geod)
    else:
        raise ValueError('earth_geod must be a string or Geod type, but instead was {0} {1}'.format(
            earth_geod, type(earth_geod)))
    geod_info = proj4_str_to_dict(earth_geod.initstring)
    a, f = geod_info['a'], geod_info['f']
    e2 = (2 - 1 * f) * f
    lat = np.pi / 180 * lat
    # Credit: https://gis.stackexchange.com/questions/75528/understanding-terms-in-length-of-degree-formula/75535#75535
    lat_dist = 2 * np.pi * a * (1 - e2) / (1 - e2 * np.sin(lat)**2)**1.5 / 360
    long_dist = 2 * np.pi * a / (1 - e2 * np.sin(lat)**2)**.5 * np.cos(lat) / 360
    return lat_dist, long_dist


def _not_none(args):
    for arg in args:
        if arg is not None:
            return True
    return False


def _create_area(lat_0, lon_0, projection='stere', area_extent=None, shape=None,
                 upper_left_extent=None, center=None, pixel_size=None, radius=None,
                 units=None, image_geod=None):
    """Creates area from given information."""
    if not isinstance(projection, str):
        raise ValueError('projection must be a string, but instead was {0} {1}'.format(
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
        raise ValueError('image_geod must be a string or Geod type, but instead was {0} {1}'.format(
            image_geod, type(image_geod)))
    proj_dict = proj4_str_to_dict('+lat_0={0} +lon_0={1} +proj={2} {3}'.format(lat_0, lon_0, projection,
                                                                               image_geod.initstring))

    area_definition = create_area_def('pywinds', proj_dict, area_extent=area_extent, shape=shape,
                           upper_left_extent=upper_left_extent, resolution=pixel_size,
                           center=center, radius=radius, units=units)
    if isinstance(area_definition, AreaDefinition):
        area_definition.area_extent = tuple(reversed(area_definition.area_extent))
    return area_definition


def _find_displacements(displacement_data=None, j=None, i=None, shape=None):
    """Retrieves pixel-displacements from a file or list."""
    if isinstance(displacement_data, str):
        # Displacement: even index, odd index. Note: (0, 0) is in the top left, i=horizontal and j=vertical.
        displacement = np.fromfile(displacement_data, dtype=np.float32)[3:]
        j_displacement = displacement[1::2]
        i_displacement = displacement[0::2]
    elif displacement_data is not None:
        if len(np.shape(displacement_data)) != 3 or np.shape(displacement_data)[0] != 2:
            raise ValueError('displacement_data should have shape (2, y, x), but instead has shape {0}'.format(
                np.shape(displacement_data)))
        j_displacement = np.array(displacement_data[1])
        i_displacement = np.array(displacement_data[0])
    else:
        return shape, 0, 0
    if shape is None:
        shape = (np.size(i_displacement)**.5, np.size(j_displacement)**.5)
        error = 'Shape was not provided and shape found from file was not comprised of integers: ' \
                '{0} pixels made a shape of {1}'.format(np.size(j_displacement) + np.size(i_displacement),
                                                        tuple([2] + list(shape)))
        shape = (_to_int(shape[0], ValueError(error)), _to_int(shape[1], ValueError(error)))
    if j is None and i is None:
        return shape, j_displacement, i_displacement
    j, i = _extrapolate_j_i(j, i, shape)
    return shape, j_displacement[j * shape[0] + i], i_displacement[j * shape[0] + i]


def _compute_lat_long(lat_0, lon_0, displacement_data=None, projection='stere', j=None, i=None,
                      area_extent=None, shape=None, upper_left_extent=None, center=None, pixel_size=None,
                      radius=None, units=None, image_geod=None):
    """Computes the latitude and longitude given an area and (j, i) values."""
    if not isinstance(lat_0, (int, float)) or not isinstance(lon_0, (int, float)):
        raise ValueError('lat_0 and lon_0 must be ints or floats, but instead were ' +
                         '{0} {1} and {2} {3} respectively'.format(
                             lat_0, type(lat_0), lon_0, type(lon_0)))
    shape, j_displacement, i_displacement, area_definition = _find_displacements_and_area(lat_0, lon_0,
                                                                                          displacement_data,
                                                                  projection=projection, j=j, i=i,
                                                                  area_extent=area_extent, shape=shape,
                                                                  upper_left_extent=upper_left_extent,
                                                                  center=center, pixel_size=pixel_size,
                                                                  radius=radius, units=units,
                                                                  image_geod=image_geod)
    if not isinstance(area_definition, AreaDefinition):
        raise ValueError('Not enough information provided to create an area definition')
    # Function that handles projection to lat/long transformation.
    p = Proj(area_definition.proj_dict, errcheck=True, preserve_units=True)
    # If i and j are None, make them cover the entire image.
    j_new, i_new = _extrapolate_j_i(j, i, shape)
    # Returns (lat, long) in degrees.
    new_lat, new_long = _reverse_param(p(*_pixel_to_pos(area_definition, j_new, i_new), errcheck=True, inverse=True))
    if np.any(j_displacement) or np.any(i_displacement):
        # Update values with displacement.
        j_old, i_old = j_new - j_displacement, i_new - i_displacement
        old_lat, old_long = _reverse_param(
            p(*_pixel_to_pos(area_definition, j_old, i_old), errcheck=True, inverse=True))
    else:
        return shape, new_lat, new_long, new_lat, new_long
    return shape, new_lat, new_long, old_lat, old_long


def _compute_vu(lat_0, lon_0, delta_time, displacement_data=None, projection='stere', j=None, i=None,
                area_extent=None, shape=None, upper_left_extent=None, center=None, pixel_size=None,
                radius=None, units=None, image_geod=None, earth_geod=None):
    if displacement_data is None:
        raise ValueError('displacement_data is required to find v and u but was not provided.')
    shape, new_lat, new_long, old_lat, old_long = _compute_lat_long(lat_0, lon_0, displacement_data=displacement_data,
                                                   projection=projection, j=j, i=i, area_extent=area_extent,
                                                   shape=shape, upper_left_extent=upper_left_extent, center=center,
                                                   pixel_size=pixel_size, radius=radius, units=units,
                                                   image_geod=image_geod)
    lat_long_distance = _lat_long_dist((new_lat + old_lat) / 2, earth_geod)
    # u = (_delta_longitude(new_long, old_long) *
    #      _lat_long_dist(old_lat, earth_geod)[1] / (delta_time * 60) +
    #      _delta_longitude(new_long, old_long) *
    #      _lat_long_dist(new_lat, earth_geod)[1] / (delta_time * 60)) / 2
    # meters/second. distance is in meters delta_time is in minutes.
    v = (new_lat - old_lat) * lat_long_distance[0] / (delta_time * 60)
    u = _delta_longitude(new_long, old_long) * lat_long_distance[1] / (delta_time * 60)
    return shape, v, u, new_lat, new_long


def _compute_velocity(lat_0, lon_0, delta_time, displacement_data=None, projection='stere', j=None, i=None,
                      area_extent=None, shape=None, upper_left_extent=None, center=None, pixel_size=None,
                      radius=None, units=None, image_geod=None, earth_geod=None):
    shape, v, u, new_lat, new_long = _compute_vu(lat_0, lon_0, delta_time, displacement_data=displacement_data,
                                           projection=projection,
                                          j=j, i=i, area_extent=area_extent, shape=shape,
                                          upper_left_extent=upper_left_extent, center=center, pixel_size=pixel_size,
                                          radius=radius, units=units, image_geod=image_geod, earth_geod=earth_geod)
    speed, angle = (u**2 + v**2)**.5, ((90 - np.arctan2(v, u) * 180 / np.pi) + 360) % 360
    # When wind vector azimuth is 0 degrees it points North (mathematically 90 degrees) and moves clockwise.
    return shape, speed, angle, v, u, new_lat, new_long


def _find_displacements_and_area(lat_0=None, lon_0=None, displacement_data=None, projection='stere', j=None, i=None,
                                 area_extent=None, shape=None, upper_left_extent=None, center=None, pixel_size=None,
                                 radius=None, units=None, image_geod=None):
    """Dynamically finds displacements and area of projection"""
    area_definition = None
    if lat_0 is not None or lon_0 is not None:
        try:
            area_definition = _create_area(lat_0, lon_0, projection=projection, area_extent=area_extent, shape=shape,
                                           upper_left_extent=upper_left_extent, center=center, pixel_size=pixel_size,
                                           radius=radius, units=units, image_geod=image_geod)
            if area_definition.height is not None and area_definition.width is not None:
                shape = (area_definition.height, area_definition.width)
        except ValueError:
            pass
    shape, j_displacement, i_displacement = _find_displacements(displacement_data, shape=shape, j=j, i=i)
    if not isinstance(area_definition, AreaDefinition) and (lat_0 is not None or lon_0 is not None):
        area_definition = _create_area(lat_0, lon_0, projection=projection, area_extent=area_extent, shape=shape,
                                       upper_left_extent=upper_left_extent, center=center, pixel_size=pixel_size,
                                       radius=radius, units=units, image_geod=image_geod)
    return shape, j_displacement, i_displacement, area_definition


def area(lat_0, lon_0, displacement_data=None, projection='stere', area_extent=None, shape=None,
         upper_left_extent=None, center=None, pixel_size=None, radius=None, units=None, image_geod=None):
    """Dynamically computes area of projection.

        Parameters
        ----------
        lat_0 : float
            Normal latitude of projection
        lon_0 : float
            Normal longitude of projection
        displacement_data : str or list, optional
            File or list containing displacements: [0, 0, 0, i11, j11, i12, j12, ...] or
            [[j_displacement], [i_displacement]] respectively. If provided, finds the
            latitude/longitude at (j,i) + displacements.
        projection : str, optional
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

        Returns
        -------
            area : AreaDefinition
                area as an AreaDefinition object
    """
    if not isinstance(lat_0, (int, float)) or not isinstance(lon_0, (int, float)):
        raise ValueError('lat_0 and lon_0 must be ints or floats, but instead were ' +
                         '{0} {1} and {2} {3} respectively'.format(
                             lat_0, type(lat_0), lon_0, type(lon_0)))
    return _find_displacements_and_area(lat_0=lat_0, lon_0=lon_0, displacement_data=displacement_data,
                                        projection=projection, area_extent=area_extent, shape=shape,
                                        upper_left_extent=upper_left_extent, center=center, pixel_size=pixel_size,
                                        radius=radius, units=units, image_geod=image_geod)[3]


def displacements(lat_0=None, lon_0=None, displacement_data=None, projection='stere', j=None, i=None,
                  area_extent=None, shape=None, upper_left_extent=None, center=None, pixel_size=None,
                  radius=None, units=None, image_geod=None, no_save=False):
    """Dynamically computes displacements.

        Parameters
        ----------
        lat_0 : float, optional
            Normal latitude of projection
        lon_0 : float, optional
            Normal longitude of projection
        displacement_data : str or list, optional
            File or list containing displacements: [0, 0, 0, i11, j11, i12, j12, ...] or
            [[j_displacement], [i_displacement]] respectively. If provided, finds the
            latitude/longitude at (j,i) + displacements.
        projection : str, optional
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
        no_save : bool
            When True, saves j_displacements to output_data/j_displacements
            and i_displacements to output_data/i_displacements

        Returns
        -------
            (j_displacements, i_displacements) : numpy.array or list
                j_displacements and i_displacements found in displacement fil or list
    """
    if displacement_data is None:
        raise ValueError('displacement_data is required to find displacements but was not provided.')
    if (not isinstance(lat_0, (int, float)) or not isinstance(lon_0, (int, float)))\
            and _not_none([lat_0, lon_0, area_extent, upper_left_extent, center, pixel_size, radius, units,
                           image_geod]):
        raise ValueError('If lat_0 or lon_0 were provided they both must be provided, but instead were ' +
                         '{0} {1} and {2} {3} respectively'.format(
                             lat_0, type(lat_0), lon_0, type(lon_0)))
    shape, j_displacement, i_displacement = _find_displacements_and_area(lat_0=lat_0, lon_0=lon_0,
                                                           displacement_data=displacement_data,
                                        projection=projection, j=j, i=i, area_extent=area_extent, shape=shape,
                                        upper_left_extent=upper_left_extent, center=center, pixel_size=pixel_size,
                                        radius=radius, units=units, image_geod=image_geod)[:3]
    if np.size(j_displacement) != 1:
        j_displacement = j_displacement.reshape(shape)
        i_displacement = i_displacement.reshape(shape)
    if no_save:
        _no_save(j_displacement, 'j_displacement', displacement_data)
        _no_save(i_displacement, 'i_displacement', displacement_data)
    return np.array((j_displacement, i_displacement))


def velocity(lat_0, lon_0, delta_time, displacement_data=None, projection='stere', j=None, i=None,
             area_extent=None, shape=None, upper_left_extent=None, center=None, pixel_size=None,
             radius=None, units=None, image_geod=None, earth_geod=None, no_save=False):
    """Computes the speed and angle of the wind given an area and pixel-displacement.

    Parameters
    ----------
    lat_0 : float
        Normal latitude of projection
    lon_0 : float
        Normal longitude of projection
    displacement_data : str or list, optional
        File or list containing displacements: [0, 0, 0, i11, j11, i12, j12, ...] or
        [[j_displacement], [i_displacement]] respectively
    projection : str, optional
        Name of projection that pixels are describing (stere, laea, merc, etc)
    j : float or None, optional
        Vertical value of pixel to find lat/long of
    i : float or None, optional
        Horizontal value of pixel to find lat/long of
    delta_time : float, optional
        Amount of time between images measured in minutes
    units : str, optional
        Units that provided arguments should be interpreted as. This can be
        one of 'deg', 'degrees', 'rad', 'radians', 'meters', 'metres', and any
        parameter supported by the
        `cs2cs -lu <https://proj4.org/apps/cs2cs.html#cmdoption-cs2cs-lu>`_
        command. Units are determined in the following priority:

        1. units expressed with each variable through a DataArray's attrs attribute
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
    image_geod : string or Geod, optional
        Spheroid of projection
    earth_geod : string or Geod, optional
        Spheroid of Earth
    no_save : bool, optional
        When True, saves speed to output_data/speed and angle to output_data/angle

    Returns
    -------
        (speed, angle) : numpy.array or list
            speed and angle (measured clockwise from north) of the wind calculated from area and pixel-displacement
    """
    shape, speed, angle = _compute_velocity(lat_0, lon_0, delta_time, displacement_data=displacement_data,
                                      projection=projection, j=j, i=i, area_extent=area_extent,
                                      shape=shape, upper_left_extent=upper_left_extent, center=center,
                                      pixel_size=pixel_size, radius=radius, units=units, image_geod=image_geod,
                                      earth_geod=earth_geod)[:3]
    if np.size(speed) != 1:
        speed = speed.reshape(shape)
        angle = angle.reshape(shape)
    if no_save is False:
        _no_save(speed, 'speed', displacement_data)
        _no_save(angle, 'angle', displacement_data)
    return np.array((speed, angle))


def vu(lat_0, lon_0, delta_time, displacement_data=None, projection='stere', j=None, i=None,
       area_extent=None, shape=None, upper_left_extent=None, center=None, pixel_size=None,
       radius=None, units=None, image_geod=None, earth_geod=None, no_save=False):
    """Computes the v and u components of the wind given an area and pixel-displacement.

    Parameters
    ----------
    lat_0 : float
        Normal latitude of projection
    lon_0 : float
        Normal longitude of projection
    displacement_data : str or list
        File or list containing displacements: [0, 0, 0, i11, j11, i12, j12, ...] or
        [[j_displacement], [i_displacement]] respectively.
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
    no_save : bool
        When True, saves v to output_data/v and u to output_data/u

    Returns
    -------
        (v, u) : numpy.array or list
            v and u components of wind calculated from area and pixel-displacement
    """
    shape, v, u = _compute_vu(lat_0, lon_0, delta_time, displacement_data=displacement_data, projection=projection,
                                j=j, i=i, area_extent=area_extent, shape=shape, upper_left_extent=upper_left_extent,
                                center=center, pixel_size=pixel_size, radius=radius, units=units, image_geod=image_geod,
                                earth_geod=earth_geod)[:3]
    if np.size(v) != 1:
        v = v.reshape(shape)
        u = u.reshape(shape)
    if no_save is False:
        _no_save(v, 'v', displacement_data)
        _no_save(u, 'u', displacement_data)
    return np.array((v, u))


def lat_long(lat_0, lon_0, displacement_data=None, projection='stere', j=None, i=None,
             area_extent=None, shape=None, upper_left_extent=None, center=None, pixel_size=None,
             radius=None, units=None, image_geod=None, no_save=False):
    """Computes the latitude and longitude given an area and (j, i) values.

    Parameters
    ----------
    lat_0 : float
        Normal latitude of projection
    lon_0 : float
        Normal longitude of projection
    displacement_data : str or list, optional
        File or list containing displacements: [0, 0, 0, i11, j11, i12, j12, ...] or
        [[j_displacement], [i_displacement]] respectively. If provided, finds the
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
        Area extent in projection units as a list (upper_right_y, upper_right_x, lower_left_y, lower_left_x)
    shape : list, optional
        Number of pixels in the y and x direction (height, width). Note that shape
        can be found from the displacement file (in such a case, shape will be square)
        or the area provided.
    upper_left_extent : list, optional
        Upper left corner of upper left pixel in projection units (y, x)
    center : list, optional
        Center of projection (lat, long)
    pixel_size : list or float, optional
        Size of pixels: (dy, dx)
    radius : list or float, optional
        Length from the center to the edges of the projection (dy, dx)
    image_geod : string or Geod
        Spheroid of projection
    no_save : bool
        When True, saves lat to output_data/latitude and long to output_data/longitude

    Returns
    -------
        (latitude, longitude) : numpy.array or list
            latitude and longitude calculated from area and pixel-displacement

    Notes
    -----
    * center will always be interpreted as degrees unless units are passed directly with center
    * The list returned is in row-column form. lat[j][i] is down j pixels and right i pixels
    """
    # If no displacements were given, then old=new
    shape, new_lat, new_long, old_lat, old_long = _compute_lat_long(lat_0, lon_0, displacement_data=displacement_data, projection=projection, j=j,
                                      i=i, area_extent=area_extent, shape=shape, upper_left_extent=upper_left_extent,
                                      center=center, pixel_size=pixel_size, radius=radius, units=units,
                                      image_geod=image_geod)
    if np.size(old_lat) != 1:
        old_lat = old_lat.reshape(shape)
        old_long = old_long.reshape(shape)
    if no_save is False:
        if displacement_data is None:
            raise ValueError('Cannot save data without displacement_data')
        else:
            if np.size(new_lat) != 1:
                new_lat = new_lat.reshape(shape)
                new_long = new_long.reshape(shape)
            _no_save(old_lat, 'old_latitude', displacement_data)
            _no_save(old_long, 'old_longitude', displacement_data)
            _no_save(new_lat, 'new_latitude', displacement_data)
            _no_save(new_long, 'new_longitude', displacement_data)
    return np.array((old_lat, old_long))


def wind_info(lat_0, lon_0, delta_time, displacement_data=None, projection='stere', j=None, i=None,
              area_extent=None, shape=None, upper_left_extent=None, center=None, pixel_size=None,
              radius=None, units=None, image_geod=None, earth_geod=None, no_save=False):
    """Computes the latitude, longitude, velocity, angle, v, and u of the wind

    Parameters
    ----------
    lat_0 : float
        Normal latitude of projection
    lon_0 : float
        Normal longitude of projection
    delta_time : int
        Amount of time that separates both files in minutes.
    displacement_data : str or list, optional
        File or list containing displacements: [0, 0, 0, i11, j11, i12, j12, ...] or
        [[j_displacement], [i_displacement]] respectively. If provided, finds the
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
        Area extent in projection units as a list (upper_right_y, upper_right_x, lower_left_y, lower_left_x)
    shape : list, optional
        Number of pixels in the y and x direction (height, width). Note that shape
        can be found from the displacement file (in such a case, shape will be square)
        or the area provided.
    upper_left_extent : list, optional
        Upper left corner of upper left pixel in projection units (y, x)
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
    no_save : bool
        When True, saves lat to output_data/latitude and long to output_data/longitude

    Returns
    -------
        (latitude, longitude, velocity, angle, v, and u at each pixel) : numpy.array or list
            latitude, longitude, velocity, angle, v, and u at each pixel
    """
    shape, speed, angle, v, u, lat, long = _compute_velocity(lat_0, lon_0, displacement_data=displacement_data,
                                                      projection=projection, j=j, i=i, delta_time=delta_time,
                                                      area_extent=area_extent, shape=shape,
                                                      upper_left_extent=upper_left_extent, center=center,
                                                      pixel_size=pixel_size, radius=radius, units=units,
                                                      image_geod=image_geod, earth_geod=earth_geod)
    # Make each variable its own column.
    winds = np.insert(np.expand_dims(np.ravel(lat), axis=1), 1, long, axis=1)
    winds = np.insert(winds, 2, speed, axis=1)
    winds = np.insert(winds, 3, angle, axis=1)
    winds = np.insert(winds, 4, v, axis=1)
    winds = np.insert(winds, 5, u, axis=1)
    if no_save is False:
        _no_save(winds, 'winds', displacement_data)
    if np.shape(winds)[0] == 1:
        winds = winds[0]
    # Columns: lat, long, speed, direction, v, u
    return winds
