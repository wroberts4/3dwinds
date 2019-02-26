from pyproj import Proj, Geod
from pyresample.utils import proj4_str_to_dict
from pyresample.geometry import AreaDefinition, DynamicAreaDefinition
from xarray import DataArray
import ntpath
import numpy as np
import os
import h5py


"""Find wind info"""


def _round(val, precision):
    if val is None:
        return None
    if isinstance(val, str):
        return val
    if np.shape(val) == ():
        return round(val, precision)
    return tuple(np.round(val, precision).tolist())


def _save_data(output_dict, displacement_filename, hdf5_group_name=None, hdf5_shape=None, area_attrs=None):
    """Saves data to a file named after the displacement_data appended with "_output"."""
    if isinstance(displacement_filename, str):
        head, tail = ntpath.split(displacement_filename)
        extension = tail or ntpath.basename(head)
    else:
        extension = 'list'
    try:
        os.mkdir(os.path.join(os.getcwd(), extension + '_output'))
    except OSError:
        pass
    hdf5 = h5py.File(os.path.join(os.getcwd(), extension + '_output', 'wind_info.hdf5'), 'a')
    if area_attrs is not None:
        file = open(os.path.join(os.getcwd(), extension + '_output', 'area.txt'), 'w')
        for attr, val in area_attrs.items():
            if val is None:
                val = 'none'
            hdf5.attrs[attr] = val
            precision = 2
            if attr == 'eccentricity':
                precision = 6
            file.write('{0}: {1}\n'.format(attr, _round(val, precision)))
        file.close()
    if hdf5_group_name is not None:
        hdf5.pop(hdf5_group_name, None)
        hdf5.create_group(hdf5_group_name)
    for name, data in output_dict.items():
        attrs = {}
        if isinstance(data, DataArray):
            attrs = data.attrs
            data = data.data
        if np.size(data) == 1:
            data = np.ravel(data)
        # np.array(np.append([0] + list(np.shape(data)), data), dtype=np.float32).tofile(os.path.join(os.getcwd(), extenion + '_output', name + '.out'))
        if hdf5_group_name is None:
            hdf5.pop(name, None)
            hdf5.create_dataset(name, data=np.array(data.reshape(hdf5_shape), dtype=np.float32))
            for attr, val in attrs.items():
                hdf5[name].attrs[attr] = val
        else:
            hdf5[hdf5_group_name].create_dataset(name, data=np.array(data.reshape(hdf5_shape), dtype=np.float32))
            for attr, val in attrs.items():
                hdf5[hdf5_group_name][name].attrs[attr] = val
        np.savetxt(os.path.join(os.getcwd(), extension + '_output', name + '.txt'), np.array(data, dtype=np.float32),
                   fmt='%.2f')
    hdf5.close()


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
    units = None
    if isinstance(param, DataArray):
        units = param.attrs.get('units', None)
        param = param.data.tolist()
    if np.shape(param) != ():
        param = list(reversed(param))
    if units is not None:
        return DataArray(param, attrs={'units': units})
    return param


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
    return np.array(position, dtype=np.float32)


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
    e2 = (2 - 1 * geod_info['f']) * geod_info['f']
    lat = np.pi / 180 * lat
    # Credit: https://gis.stackexchange.com/questions/75528/understanding-terms-in-length-of-degree-formula/75535#75535
    lat_dist = 2 * np.pi * geod_info['a'] * (1 - e2) / (1 - e2 * np.sin(lat)**2)**1.5 / 360
    long_dist = 2 * np.pi * geod_info['a'] / (1 - e2 * np.sin(lat)**2)**.5 * np.cos(lat) / 360
    return lat_dist, long_dist


def _not_none(args):
    for arg in args:
        if arg is not None:
            return True
    return False


# TODO: USE CREATE_AREA WHEN RELEASES: from pyresample import create_area_def
def _create_area(lat_0, lon_0, projection='stere', area_extent=None, shape=None,
                 upper_left_extent=None, center=None, pixel_size=None, radius=None,
                 units=None, image_geod=None):
    """Creates area from given information."""
    if not isinstance(projection, str):
        raise ValueError('projection must be a string, but instead was {0} {1}'.format(
            projection, type(projection)))
    if units is not None or radius is not None or upper_left_extent is not None:
        raise ValueError('radius, upper_left_extent, and units are not yet supported')
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
    # if center is not None and not isinstance(center, DataArray):
    #     center = DataArray(center, attrs={'units': 'degrees'})
    if image_geod is None:
        image_geod = Geod(ellps='WGS84')
    elif isinstance(image_geod, str):
        image_geod = Geod(ellps=image_geod)
    else:
        raise ValueError('image_geod must be a string or Geod type, but instead was {0} {1}'.format(
            image_geod, type(image_geod)))
    proj_dict = proj4_str_to_dict('+lat_0={0} +lon_0={1} +proj={2} {3}'.format(lat_0, lon_0, projection,
                                                                               image_geod.initstring))
    # TODO: REMOVE THIS WHEN PYRESAMPLE MAKES NEW RELEASE.
    if area_extent is None and center is not None and pixel_size is not None and shape is not None:
        center = Proj(proj_dict)(*center, error_check=True)
        area_extent = [center[0] - pixel_size * shape[1] / 2, center[1] - pixel_size * shape[0] / 2,
                       center[0] + pixel_size * shape[1] / 2, center[1] + pixel_size * shape[0] / 2]
    if shape is None and pixel_size is not None and area_extent is not None:
        shape = (area_extent[3] - area_extent[1]) / pixel_size, (area_extent[2] - area_extent[0]) / pixel_size
    if area_extent is not None and shape is not None:
        area_definition = AreaDefinition('pywinds', 'pywinds', '', proj_dict, shape[1], shape[0], area_extent)
    elif shape is not None:
        area_definition = DynamicAreaDefinition(projection=proj_dict, width=shape[1], height=shape[0])
    elif area_extent is not None:
        area_definition = DynamicAreaDefinition(projection=proj_dict, area_extent=area_extent)
    else:
        raise ValueError('Not enough information provided to create an area definition')
    # area_definition = create_area_def('pywinds', proj_dict, area_extent=area_extent, shape=shape,
    #                        upper_left_extent=upper_left_extent, resolution=pixel_size,
    #                        center=center, radius=radius, units=units)
    return area_definition


def _find_displacements(displacement_data=None, j=None, i=None, shape=None):
    """Retrieves pixel-displacements from a file or list."""
    if isinstance(displacement_data, str):
        # Displacement: even index, odd index. Note: (0, 0) is in the top left, i=horizontal and j=vertical.
        shape = np.fromfile(displacement_data, dtype=int)[1:3]
        displacement = np.fromfile(displacement_data, dtype=np.float32)[3:]
        j_displacement = displacement[1::2]
        i_displacement = displacement[0::2]
        if (shape[0] is 0 or shape[1] != np.size(j_displacement) / shape[0] or
                shape[1] != np.size(i_displacement) / shape[0]):
            shape = None
    elif displacement_data is not None:
        if len(np.shape(displacement_data)) != 2 and len(np.shape(displacement_data)) != 3 or np.shape(displacement_data)[0] != 2:
            raise ValueError('displacement_data should have shape (2, y * x) or (2, y, x), but instead has shape {0}'.format(
                np.shape(displacement_data)))
        if len(np.shape(displacement_data)) != 2:
            displacement_data = np.reshape(displacement_data, (2, int(np.size(displacement_data) / 2)))
        j_displacement = np.array(displacement_data[0], dtype=np.float32)
        i_displacement = np.array(displacement_data[1], dtype=np.float32)
    else:
        return shape, 0, 0
    if shape is None:
        shape = [np.size(i_displacement)**.5, np.size(j_displacement)**.5]
        error = 'Shape was not provided and shape found from file was not comprised of integers: ' \
                '{0} pixels made a shape of {1}'.format(np.size(j_displacement) + np.size(i_displacement),
                                                        tuple([2] + shape))
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
         upper_left_extent=None, center=None, pixel_size=None, radius=None, units=None, image_geod=None, no_save=False):
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
    area_definition = _find_displacements_and_area(lat_0=lat_0, lon_0=lon_0, displacement_data=displacement_data,
                                        projection=projection, area_extent=area_extent, shape=shape,
                                        upper_left_extent=upper_left_extent, center=center, pixel_size=pixel_size,
                                        radius=radius, units=units, image_geod=image_geod)[3]
    p = Proj(area_definition.proj_dict, errcheck=True, preserve_units=True)
    projection = area_definition.proj_dict['proj']
    a = area_definition.proj_dict['a']
    f = area_definition.proj_dict['f']
    area_extent = _reverse_param(area_definition.area_extent)
    if area_extent is not None:
        center = ((area_extent[0] + area_extent[2]) / 2, (area_extent[1] + area_extent[3]) / 2)
        center = _reverse_param(p(*_reverse_param(center), inverse=True))
        area_extent = _reverse_param(p(*_reverse_param(area_extent[:2]), inverse=True)) +\
                      _reverse_param(p(*_reverse_param(area_extent[2:]), inverse=True))
    else:
        center = None
        area_extent = None
    if area_definition.height is None or area_definition.width is None:
        shape = None
    else:
        shape = (area_definition.height, area_definition.width)
    try:
        pixel_size = (area_definition.pixel_size_y, area_definition.pixel_size_x)
    except AttributeError:
        pixel_size = area_definition.resolution

    area_data = {'projection': projection, 'lat_0': lat_0, 'lon_0': lon_0, 'equatorial radius': a,
                 'eccentricity': f, 'shape': shape, 'area_extent': area_extent, 'pixel_size': pixel_size,
                 'center': center}

    if no_save is False:
        if displacement_data is None:
            raise ValueError('Cannot save data without displacement_data')
        _save_data({}, displacement_data, area_attrs=area_data)
    return area_data


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
        j_displacement = np.array(j_displacement.reshape(shape), dtype=np.float32)
        i_displacement = np.array(i_displacement.reshape(shape), dtype=np.float32)
    if no_save is False:
        _save_data({'j_displacement': j_displacement, 'i_displacement': i_displacement},
                    displacement_data, hdf5_group_name='displacements')
    return np.array((j_displacement, i_displacement), dtype=np.float32)


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
        speed = np.array(speed.reshape(shape), dtype=np.float32)
        angle = np.array(angle.reshape(shape), dtype=np.float32)
    if no_save is False:
        _save_data({'speed': DataArray(speed, attrs={'units': 'meters/second'}),
                  'angle': DataArray(angle, attrs={'units': 'degrees'})},
                 displacement_data, hdf5_group_name='velocity')
    return np.array((speed, angle), dtype=np.float32)


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
        v = np.array(v.reshape(shape), dtype=np.float32)
        u = np.array(u.reshape(shape), dtype=np.float32)
    if no_save is False:
        _save_data({'v': DataArray(v, attrs={'units': 'meters/second'}),
                  'u': DataArray(u, attrs={'units': 'meters/second'})},
                 displacement_data, hdf5_group_name='vu')
    return np.array((v, u), dtype=np.float32)


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
        old_lat = np.array(old_lat.reshape(shape), dtype=np.float32)
        old_long = np.array(old_long.reshape(shape), dtype=np.float32)
    if no_save is False:
        if displacement_data is None:
            raise ValueError('Cannot save data without displacement_data')
        if np.size(new_lat) != 1:
            new_lat = np.array(new_lat.reshape(shape), dtype=np.float32)
            new_long = np.array(new_long.reshape(shape), dtype=np.float32)
        _save_data({'old_latitude': DataArray(old_lat, attrs={'units': 'degrees'}),
                  'old_longitude': DataArray(old_long, attrs={'units': 'degrees'}),
                  'new_latitude': DataArray(new_lat, attrs={'units': 'degrees'}),
                  'new_longitude': DataArray(new_long, attrs={'units': 'degrees'})},
                 displacement_data, hdf5_group_name='lat_long')
    return np.array((old_lat, old_long), dtype=np.float32)


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
        File or list containing displacements: [tag, nx, ny, i11, j11, i12, j12, ...] or
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
    winds = np.array(winds, dtype=np.float32)
    if no_save is False:
        if np.shape(winds)[0] == 1:
            shape = [6]
            winds = winds[0]
        else:
            shape = list(shape) + [6]
        _save_data({'wind_info': DataArray(winds, attrs={'description': 'new_lat (degrees), new_long (degrees), '
                                                       'speed (meters/second), angle (degrees), v (meters/second), '
                                                       'u (meters/second)'})},
                 displacement_data, hdf5_shape=shape)
    # Columns: lat, long, speed, direction, v, u
    return winds
