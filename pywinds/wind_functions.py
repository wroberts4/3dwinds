"""Calculates area information, j and i displacement, new and old latitude/longitude, v, u, and velocity of the wind."""
import logging
import ntpath
import os
import datetime
import struct

import numpy as np
import xarray
from pyproj import Geod, Proj
from pyresample.area_config import create_area_def
from pyresample.geometry import AreaDefinition, DynamicAreaDefinition
from pyresample.utils import proj4_str_to_dict

from pywinds.wrapper_utils import area_to_string

logger = logging.getLogger(__name__)


def _save_data(save_directory, data_list, text_shape=None, mode='a'):
    """Handles text and netcdf4 file saving"""
    if mode == 'a' and not os.path.exists(save_directory):
        logger.warning('Data not saved to {0}: Save directory does not exist'.format(save_directory))
        return
    # Get name of displacement file (without path). If string is not a file, return and don't make a file.
    try:
        os.makedirs(save_directory)
    except OSError:
        pass
    # Formulate all the datasets into a single dict of float32 to be passed to xarray.Dataset.
    dataset_dict = {}
    encoding = {}
    for data in data_list:
        dataset_dict[data.name] = data
        encoding[data.name] = {'dtype': np.float32}
        # Text file handling. This takes A LOT of time.
        text_path = os.path.join(save_directory, data.name + '.txt')
        if None not in data.data:
            data = data.data
            if np.size(data) == 1:
                data = np.ravel(data)
            np.savetxt(text_path, data.reshape(text_shape), fmt='%.2f', delimiter=',')
        # Area definition.
        else:
            data = data.attrs
            with open(text_path, 'w') as file:
                file.write(area_to_string(data))
            #  Change any null data to a string or else an exception is raised.
            for key, val in data.items():
                if val is None:
                    data[key] = 'None'
    netcdf4_path = os.path.join(save_directory, 'wind_info.nc')
    xarray.Dataset(dataset_dict, attrs={'Conventions': 'CF-1.7'}).to_netcdf(netcdf4_path, mode=mode,
                                                                            encoding=encoding)
    if mode == 'w':
        logger.debug('Save directory and wind_info.nc created successfully')
    else:
        logger.debug('Data saved successfully')


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


def _reverse_params(params):
    """Reverses the order of parameters (y/x-form is given, but most packages need x/y-form."""
    reversed_params = []

    for param in params:
        units = None
        if isinstance(param, xarray.DataArray):
            units = param.attrs.get('units', None)
            param = param.data.tolist()
        if np.shape(param) != ():
            param = list(reversed(param))
        if units is not None:
            param = xarray.DataArray(param, attrs={'units': units})
        reversed_params.append(param)
    return reversed_params


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
    return position


def _sin(angle):
    """"Sine function that takes degrees"""
    return np.sin(np.radians(angle))


def _cos(angle):
    """"Cosine function that takes degrees"""
    return np.cos(np.radians(angle))


def _tan(angle):
    """"Tangent function that takes degrees"""
    return np.tan(np.radians(angle))


def _arctanh(x):
    """"Hyperarctangent function that outputs degrees"""
    return np.degrees(np.arctanh(x))


def _arctan2(x, y):
    """"atan2 function that outputs degrees"""
    return np.degrees(np.arctan2(x, y))


def _make_ellipsoid(ellipsoid, var_name):
    from pyproj import transform
    if ellipsoid is None:
        geod_info = Geod(ellps='WGS84')
    elif isinstance(ellipsoid, str):
        geod_info = Geod(ellps=ellipsoid)
    elif isinstance(ellipsoid, dict):
        for key in ellipsoid.keys():
            if key not in ['a', 'b', 'rf', 'e', 'f', 'es']:
                logger.warning('Invalid parameter passed to ellipsoid: {0}'.format(key))
        if 'a' not in ellipsoid:
            if 'b' not in ellipsoid:
                logger.warning('Neither the major axis (a) nor the minor axis (b) were provided')
            else:
                if 'rf' in ellipsoid:
                    ellipsoid['f'] = 1 / ellipsoid['rf']
                if 'e' in ellipsoid:
                    ellipsoid['es'] = ellipsoid['e'] ** 2
                if 'f' in ellipsoid:
                    if ellipsoid['f'] < 0 or ellipsoid['f'] >= 1:
                        raise ValueError('Invalid flattening of {0}: 0 <= flattening < 1'.format(ellipsoid['f']))
                    ellipsoid['a'] = ellipsoid['b'] / (1 - ellipsoid['f'])
                elif 'es' in ellipsoid:
                    if ellipsoid['es'] < 0 or ellipsoid['es'] >= 1:
                        raise ValueError('Invalid eccentricity of {0}: 0 <= eccentricity < 1'.format(ellipsoid['es']))
                    ellipsoid['a'] = ellipsoid['b'] / (1 - ellipsoid['es']) ** .5
                else:
                    ellipsoid['a'] = ellipsoid['b']
        for key, val in ellipsoid.items():
            if hasattr(val, 'units'):
                if key in ['a', 'b']:
                    val.attrs['units'] =\
                        'm' if val.attrs['units'] == 'meters' or val.attrs['units'] == 'metres' else val.attrs['units']
                    ellipsoid[key] = transform(Proj({'proj': 'stere', 'units': val.attrs['units']}),
                                               Proj({'proj': 'stere', 'units': 'm'}), val, 0)[0]
                else:
                    logger.warning('Only a and b have units, but {0} was provided {1}'.format(key, val.attrs['units']))
                    ellipsoid[key] = val.data
        geod_info = Geod(**ellipsoid)
    else:
        raise ValueError('{0} must be a string or Geod type, but instead was {1} {2}'.format(var_name, ellipsoid,
                                                                                             type(ellipsoid)))
    if geod_info.a < 0:
        raise ValueError('Invalid major axis of {0}: Negative numbers not allowed'.format(geod_info.a))
    if geod_info.f < 0 or geod_info.f >= 1:
        raise ValueError('Invalid flattening of {0}: 0 <= flattening < 1'.format(geod_info.f))
    return geod_info


def _delta_longitude(new_long, old_long):
    """Calculates the change in longitude on the Earth. Units are in degrees"""
    delta_long = new_long - old_long
    delta_long = np.where(delta_long < 360, delta_long, delta_long % 360)
    delta_long = np.where(delta_long > -360, delta_long, delta_long % -360)
    delta_long = np.where(delta_long < 180, delta_long, delta_long - 360)
    delta_long = np.where(delta_long > -180, delta_long, delta_long + 360)
    return delta_long


def _not_none(args):
    for arg in args:
        if arg is not None:
            return True
    return False


def _create_area(lat_ts, lat_0, long_0, projection=None, area_extent=None, shape=None, center=None, pixel_size=None,
                 upper_left_extent=None, radius=None, projection_ellipsoid=None, units=None, displacement_data=None,
                 no_save=True, save_directory=None):
    """Creates area from given information."""
    if projection is None:
        projection = 'stere'
    if units is None:
        units = 'm'
    geod_info = _make_ellipsoid(projection_ellipsoid, 'projection_ellipsoid')
    logger.debug('Projection ellipsoid data: {0}'.format(geod_info.initstring.replace('+', '')))
    # Center is given in (lat, long) order, but create_area_def needs it in (long, lat) order.
    if area_extent is not None:
        area_extent_ll, area_extent_ur = area_extent[0:2], area_extent[2:4]
    else:
        area_extent_ll, area_extent_ur = None, None
    center, pixel_size, upper_left_extent, radius, area_extent_ll, area_extent_ur = _reverse_params(
        [center, pixel_size, upper_left_extent, radius, area_extent_ll, area_extent_ur])
    if area_extent is not None:
        # Needs order [ll_x, ll_y, ur_x, ur_y].
        if isinstance(area_extent, xarray.DataArray):
            area_extent_ll = area_extent_ll.data.tolist()
            area_extent_ur = area_extent_ur.data.tolist()
            area_extent = xarray.DataArray(area_extent_ll + area_extent_ur, attrs=area_extent.attrs)
        else:
            area_extent = area_extent_ll + area_extent_ur
    # Makes center defualt to degrees
    if center is not None and not isinstance(center, xarray.DataArray):
        center = xarray.DataArray(center, attrs={'units': 'degrees'})
    proj_dict = proj4_str_to_dict(
        '+lat_ts={0} +lat_0={1} +lon_0={2} +proj={3} {4}'.format(lat_ts, lat_0, long_0, projection,
                                                                 geod_info.initstring))
    # Object that contains area information.
    area_definition = create_area_def('pywinds', proj_dict, area_extent=area_extent, shape=shape, resolution=pixel_size,
                                      center=center, upper_left_extent=upper_left_extent, radius=radius, units=units)

    # Below is logic for printing and saving data.
    area_extent = area_definition.area_extent
    # Function that handles projection to lat/long transformation.
    p = Proj(proj_dict)
    if area_extent is not None:
        center = ((area_extent[1] + area_extent[3]) / 2, (area_extent[0] + area_extent[2]) / 2)
        # Both in degrees
        center = _reverse_params([p(center[1], center[0], inverse=True)])[0]
        # Needs order [ll_x, ll_y, ur_x, ur_y]
        area_extent = _reverse_params([p(area_extent[0], area_extent[1], inverse=True)])[0] + \
            _reverse_params([p(area_extent[2], area_extent[3], inverse=True)])[0]
        if area_extent[2] - area_extent[0] < 0 or area_extent[3] - area_extent[1] < 0:
            logger.warning('invalid area_extent. Lower left corner is above or to the right of the upper right corner:'
                           '{0}'.format(area_extent))
    else:
        center = None
    shape = [area_definition.height, area_definition.width]
    shape = None if None in shape else shape
    if isinstance(area_definition, AreaDefinition):
        pixel_size = [area_definition.pixel_size_y, area_definition.pixel_size_x]
    elif isinstance(area_definition, DynamicAreaDefinition):
        pixel_size = area_definition.resolution
    else:
        pixel_size = None
    a = proj_dict.get('a')
    f = proj_dict.get('f')
    b = a * (1 - f)
    e = (1 - b ** 2 / a ** 2) ** .5
    if abs(f) > 0.0:
        i_f = 1 / f
    else:
        i_f = 0
    if no_save is False:
        if displacement_data is None:
            raise ValueError('Cannot save data without displacement_data')
        up_longitude = p(0, 100, inverse=True)[0]
        if up_longitude == 180:
            up_longitude = -180.0
        # Credit: http://earth-info.nga.mil/GandG/coordsys/polar_stereographic/Polar_Stereo_phi1_from_k0_memo.pdf
        k90 = ((1 + e) ** (1 + e) * (1 - e) ** (1 - e)) ** .5
        k0 = ((1 + _sin(lat_ts)) / 2 * k90 /
              ((1 + e * _sin(lat_ts)) ** (1 + e) * (1 - e * _sin(lat_ts)) ** (1 - e)) ** .5)
        attrs = {'straight_vertical_longitude_from_pole': up_longitude, 'latitude_of_projection_origin': float(lat_0),
                 'scale_factor_at_projection_origin': k0, 'standard_parallel': float(lat_ts),
                 'resolution_at_standard_parallel': np.ravel(pixel_size)[0], 'false_easting': 0.0,
                 'false_northing': 0.0, 'semi_major_axis': a, 'semi_minor_axis': b, 'inverse_flattening': i_f}
        logger.debug('Saving known area information')
        _save_data(save_directory, [xarray.DataArray(None, name='polar_stereographic', attrs=attrs)])
    return {'projection': projection, 'lat-ts': lat_ts, 'lat-0': lat_0, 'long-0': long_0, 'equatorial-radius': a,
            'eccentricity': e, 'inverse-flattening': i_f, 'shape': shape, 'area-extent': area_extent,
            'pixel-size': pixel_size, 'center': center}, area_definition


def _find_displacements(displacement_data=None, j=None, i=None, shape=None, no_save=True, save_directory=None):
    """Retrieves pixel-displacements from a 32-bit float binary file or list."""
    if isinstance(displacement_data, str):
        try:
            # Displacement: even index, odd index. Note: (0, 0) is in the top left, i=horizontal and j=vertical.
            # Convert 32 float to 64 float to prevent rounding errors.
            displacement = np.array(np.fromfile(displacement_data, dtype=np.float32)[3:], dtype=np.float64)
        except FileNotFoundError:
            logger.warning('displacement_data is required, but was not found or provided')
        with open(displacement_data, mode='rb') as file:
            data = file.read()
            file_shape = struct.unpack("ii", data[4:12])
            tag = struct.unpack("cccc", data[:4])
            # tag == 'PIEH'. Not used, but may be useful to others.
            tag = ''.join([char.decode("utf-8") for char in tag])
        logger.info('Reading displacements from {0}'.format(displacement_data))
        # displacement will be defined since open(displacement_data, mode='rb') will throw an error otherwise.
        j_displacement = displacement[1::2]
        i_displacement = displacement[0::2]
        if (file_shape[0] is not 0 and file_shape[1] == np.size(j_displacement) / file_shape[0] and
                file_shape[1] == np.size(i_displacement) / file_shape[0]):
            if shape is not None and shape != file_shape:
                logger.warning('Shape found\nfrom area or provided by user does not match the shape '
                               'of the file:\n{0} vs {1}'.format(shape, file_shape))
            elif shape is None:
                logger.debug('Native shape of file found {0}'.format(file_shape))
                shape = file_shape
    # List handling
    elif displacement_data is not None:
        logger.debug('Reading displacements from a list')
        if len(np.shape(displacement_data)) != 2 and len(np.shape(displacement_data)) != 3 or \
                np.shape(displacement_data)[0] != 2:
            raise ValueError(
                'displacement_data should have shape (2, y * x) or (2, y, x), but instead has shape {0}'.format(
                    np.shape(displacement_data)))
        if len(np.shape(displacement_data)) != 2:
            displacement_data = np.reshape(displacement_data, (2, int(np.size(displacement_data) / 2)))
        j_displacement = np.array(displacement_data[0], dtype=np.float64)
        i_displacement = np.array(displacement_data[1], dtype=np.float64)
    # Used for new lat/long
    else:
        return shape, 0.0, 0.0
    # Try to find shape by "squaring" file.
    if shape is None:
        logger.info('No shape could be found, attempting to find square shape of data')
        shape = [np.size(i_displacement) ** .5, np.size(j_displacement) ** .5]
        error = 'Shape was not provided and shape found from file was not comprised of integers: ' \
                '{0} pixels made a shape of {1}'.format(np.size(j_displacement) + np.size(i_displacement),
                                                        tuple([2] + shape))
        shape = (_to_int(shape[0], ValueError(error)), _to_int(shape[1], ValueError(error)))
    if shape is not None and shape[0] != shape[1]:
        logger.debug('Shape given or found is not square {0}'.format(shape))
    # Make sure shape matches the displacement shape.
    if shape[0] is 0 or shape[1] != np.size(j_displacement) / shape[0]:
        raise ValueError(
            'Could not reshape displacement data of size {0} to shape {1}'.format(np.size(j_displacement), shape))
    if shape[0] is 0 or shape[1] != np.size(i_displacement) / shape[0]:
        raise ValueError(
            'Could not reshape displacement data of size {0} to shape {1}'.format(np.size(i_displacement), shape))
    if j is not None or i is not None:
        j, i = _extrapolate_j_i(j, i, shape)
        j_displacement, i_displacement = j_displacement[j * shape[0] + i], i_displacement[j * shape[0] + i]
    if no_save is False:
        dims = None
        if np.size(j_displacement) != 1:
            dims = ['y', 'x']
        logger.debug('Saving displacements')
        _save_data(save_directory, (
            xarray.DataArray(_reshape(j_displacement, shape), name='j_displacement', dims=dims,
                             attrs={'standard_name': 'divergence_of_wind',
                                    'description': 'vertical pixel displacement at each pixel',
                                    'grid_mapping_name': 'polar_stereographic'}),
            xarray.DataArray(_reshape(i_displacement, shape), name='i_displacement', dims=dims,
                             attrs={'standard_name': 'divergence_of_wind',
                                    'description': 'horizontal pixel displacement at each pixel',
                                    'grid_mapping_name': 'polar_stereographic'})))
    return shape, j_displacement, i_displacement


def _reshape(array, shape):
    """Easier way to handle list and number format in one method."""
    if np.size(array) == 1:
        return array
    return np.reshape(array, shape)


def _compute_lat_long(lat_ts, lat_0, long_0, displacement_data=None, projection=None, j=None, i=None,
                      area_extent=None, shape=None, center=None, pixel_size=None, upper_left_extent=None, radius=None,
                      units=None, projection_ellipsoid=None, no_save=True, save_directory=None):
    """Computes the latitude and longitude given an area and (j, i) values."""
    if not isinstance(lat_0, (int, float)) or not isinstance(long_0, (int, float)):
        raise ValueError(
            'lat_0 and long_0 must be ints or floats, but instead were ' + '{0} {1} and {2} {3} respectively'.format(
                lat_0, type(lat_0), long_0, type(long_0)))
    shape, j_displacement, i_displacement, area_definition = \
        _find_displacements_and_area(lat_ts=lat_ts, lat_0=lat_0, long_0=long_0, displacement_data=displacement_data,
                                     projection=projection, j=j, i=i, area_extent=area_extent, shape=shape,
                                     center=center, pixel_size=pixel_size, upper_left_extent=upper_left_extent,
                                     radius=radius, units=units, projection_ellipsoid=projection_ellipsoid,
                                     no_save=no_save, save_directory=save_directory)[:4]
    if not isinstance(area_definition, AreaDefinition):
        raise ValueError('Not enough information provided to create an area for projection')
    logger.debug('All area data found')
    logger.debug('Finding latitudes and longitudes')
    # Function that handles projection to lat/long transformation.
    p = Proj(area_definition.proj_dict, errcheck=True, preserve_units=True)
    # If i and j are None, make them cover the entire image.
    j_new, i_new = _extrapolate_j_i(j, i, shape)
    # Returns (lat, long) in degrees.
    new_long, new_lat = p(*_pixel_to_pos(area_definition, j_new, i_new), errcheck=True, inverse=True)
    if np.any(j_displacement) or np.any(i_displacement):
        # Update values with displacement.
        j_old, i_old = j_new - j_displacement, i_new - i_displacement
        old_long, old_lat = p(*_pixel_to_pos(area_definition, j_old, i_old), errcheck=True, inverse=True)
    else:
        old_lat = new_lat
        old_long = new_long
    if no_save is False:
        if displacement_data is None:
            raise ValueError('Cannot save data without displacement_data')
        dims = None
        if np.size(old_lat) != 1:
            dims = ['y', 'x']
        logger.debug('Saving lat_long')
        _save_data(save_directory, (xarray.DataArray(_reshape(new_lat, shape), name='new_latitude', dims=dims,
                                                     attrs={'standard_name': 'latitude',
                                                            'grid_mapping_name': 'polar_stereographic',
                                                            'units': 'degrees'}),
                                    xarray.DataArray(_reshape(new_long, shape), name='new_longitude', dims=dims,
                                                     attrs={'standard_name': 'longitude',
                                                            'grid_mapping_name': 'polar_stereographic',
                                                            'units': 'degrees'}),
                                    xarray.DataArray(_reshape(old_lat, shape), name='old_latitude', dims=dims,
                                                     attrs={'standard_name': 'latitude',
                                                            'grid_mapping_name': 'polar_stereographic',
                                                            'units': 'degrees'}),
                                    xarray.DataArray(_reshape(old_long, shape), name='old_longitude', dims=dims,
                                                     attrs={'standard_name': 'longitude',
                                                            'grid_mapping_name': 'polar_stereographic',
                                                            'units': 'degrees'})))
    return shape, new_lat, new_long, old_lat, old_long


def _compute_velocity(lat_ts, lat_0, long_0, delta_time, displacement_data=None, projection=None, j=None, i=None,
                      area_extent=None, shape=None, center=None, pixel_size=None, upper_left_extent=None, radius=None,
                      units=None, projection_ellipsoid=None, earth_ellipsoid=None, no_save=True, save_directory=None):
    shape, new_lat, new_long, old_lat, old_long = _compute_lat_long(lat_ts, lat_0, long_0,
                                                                    displacement_data=displacement_data,
                                                                    projection=projection, j=j, i=i,
                                                                    area_extent=area_extent, shape=shape, center=center,
                                                                    pixel_size=pixel_size,
                                                                    upper_left_extent=upper_left_extent, radius=radius,
                                                                    units=units,
                                                                    projection_ellipsoid=projection_ellipsoid,
                                                                    no_save=no_save, save_directory=save_directory)
    logger.debug('Calculating speed and angle (velocity)')
    distance, angle = loxodrome_bck(old_lat, old_long, new_lat, new_long, earth_ellipsoid=earth_ellipsoid)[:2]
    speed = distance / (delta_time * 60)
    if no_save is False:
        dims = None
        if np.size(speed) != 1:
            dims = ['y', 'x']
        logger.debug('Saving velocity')
        _save_data(save_directory, (xarray.DataArray(_reshape(speed, shape), name='speed', dims=dims,
                                                     attrs={'standard_name': 'wind_speed',
                                                            'grid_mapping_name': 'polar_stereographic',
                                                            'units': 'm/s'}),
                                    xarray.DataArray(_reshape(angle, shape), name='angle', dims=dims,
                                                     attrs={'standard_name': 'wind_to_direction',
                                                            'grid_mapping_name': 'polar_stereographic',
                                                            'units': 'degrees',
                                                            'description': 'Forward bearing of rhumb line'})))
    # When wind vector bearing is 0 degrees it points North (mathematically 90 degrees) and moves clockwise.
    # speed is in meters/second.
    return shape, speed, angle, new_lat, new_long


def _compute_vu(lat_ts, lat_0, long_0, delta_time, displacement_data=None, projection=None, j=None, i=None,
                area_extent=None, shape=None, center=None, pixel_size=None, upper_left_extent=None, radius=None,
                units=None, projection_ellipsoid=None, earth_ellipsoid=None, no_save=True, save_directory=None):
    shape, speed, angle, new_lat, new_long = _compute_velocity(lat_ts, lat_0, long_0, delta_time,
                                                               displacement_data=displacement_data,
                                                               projection=projection, j=j, i=i, area_extent=area_extent,
                                                               shape=shape, center=center, pixel_size=pixel_size,
                                                               upper_left_extent=upper_left_extent, radius=radius,
                                                               units=units, projection_ellipsoid=projection_ellipsoid,
                                                               earth_ellipsoid=earth_ellipsoid, no_save=no_save,
                                                               save_directory=save_directory)
    logger.debug('Finding v and u components')
    # IMPORTANT, THIS IS CORRECT: Since angle is measured counter-cloclwise from north, then v = sin(pi - angle) and
    # u = cos(pi - angle). sin(pi - angle) = cos(angle) and cos(pi - angle) = sin(angle)!
    v = _cos(angle) * speed
    u = _sin(angle) * speed
    if no_save is False:
        dims = None
        if np.size(v) != 1:
            dims = ['y', 'x']
        logger.debug('Saving vu')
        _save_data(save_directory, (xarray.DataArray(_reshape(v, shape), name='v', dims=dims,
                                                     attrs={'standard_name': 'northward_wind',
                                                            'grid_mapping_name': 'polar_stereographic',
                                                            'units': 'm/s'}),
                                    xarray.DataArray(_reshape(u, shape), name='u', dims=dims,
                                                     attrs={'standard_name': 'eastward_wind',
                                                            'grid_mapping_name': 'polar_stereographic',
                                                            'units': 'm/s'})))
    return shape, v, u, speed, angle, new_lat, new_long


def _find_displacements_and_area(lat_ts=None, lat_0=None, long_0=None, displacement_data=None, projection=None,
                                 j=None, i=None, area_extent=None, shape=None, center=None, pixel_size=None,
                                 upper_left_extent=None, radius=None, units=None, projection_ellipsoid=None,
                                 no_save=True, save_directory=None):
    """Dynamically finds displacements and area of projection"""
    area_definition = None
    area_data = None
    # Allows just displacements to be called without raising an area not found axception.
    has_area_args = _not_none([lat_ts, lat_0, long_0, projection, area_extent, center, pixel_size,
                               upper_left_extent, radius, units, projection_ellipsoid])
    # Try to get shape from area.
    if has_area_args:
        if None in [lat_ts, lat_0, long_0]:
            logger.warning('Area information provided but at least one of lat_ts, lat_0, or long_0 was not defined')
        try:
            logger.debug('Finding area information before reading displacements')
            area_data, area_definition = _create_area(lat_ts, lat_0, long_0, projection=projection,
                                                      area_extent=area_extent, shape=shape, center=center,
                                                      pixel_size=pixel_size, upper_left_extent=upper_left_extent,
                                                      radius=radius, units=units,
                                                      projection_ellipsoid=projection_ellipsoid,
                                                      displacement_data=displacement_data, no_save=no_save,
                                                      save_directory=save_directory)
            if area_definition.height is not None and area_definition.width is not None:
                shape = (area_definition.height, area_definition.width)
        # Lets area fail after finding/saving displacements.
        except ValueError:
            logger.warning('Error in creating an area')
            _find_displacements(displacement_data, shape=shape, j=j, i=i, no_save=no_save,
                                save_directory=save_directory)
            raise
    shape, j_displacement, i_displacement = _find_displacements(displacement_data, shape=shape, j=j, i=i,
                                                                no_save=no_save, save_directory=save_directory)
    # Either tries to find area with shape found from file, or displays ValueError if excepted above.
    if has_area_args and None in (area_definition.height, area_definition.width):
        logger.debug('Incomplete area information provided')
        logger.debug('Using shape found from displacement_data to try to make an area definition')
        area_data, area_definition = _create_area(lat_ts, lat_0, long_0, projection=projection, area_extent=area_extent,
                                                  shape=shape, center=center, pixel_size=pixel_size,
                                                  upper_left_extent=upper_left_extent, radius=radius, units=units,
                                                  projection_ellipsoid=projection_ellipsoid,
                                                  displacement_data=displacement_data, no_save=no_save,
                                                  save_directory=save_directory)
    # If area is still not defined, try to use projection center as area center.
    if has_area_args and area_definition.area_extent is None and center is None:
        logger.debug('Incomplete area information provided')
        logger.debug('Using lat_0 and long_0 as center to try to make an area definition')
        area_data, area_definition = _create_area(lat_ts, lat_0, long_0, projection=projection, area_extent=area_extent,
                                                  shape=shape, center=(lat_0, long_0), pixel_size=pixel_size,
                                                  upper_left_extent=upper_left_extent, radius=radius, units=units,
                                                  projection_ellipsoid=projection_ellipsoid,
                                                  displacement_data=displacement_data, no_save=no_save,
                                                  save_directory=save_directory)
    # list, list, list, AreaDefinition, dict
    return shape, j_displacement, i_displacement, area_definition, area_data


def area(lat_ts, lat_0, long_0, displacement_data=None, projection=None, area_extent=None, shape=None, center=None,
         pixel_size=None, upper_left_extent=None, radius=None, units=None, projection_ellipsoid=None):
    """Dynamically computes area of projection.

    Parameters
    ----------
    lat_ts: float
        Latitude  of true scale
    lat_0 : float
        Latitude of origin
    long_0 : float
        Central meridian
    displacement_data : str or list, optional
        Filename or list containing displacements: [tag, width, height, i_11, j_11, i_12, j_12, ..., i_nm, j_nm] or
        [[j_displacement], [i_displacement]] respectively
    projection : str
        Name of projection that pixels are describing (stere, laea, merc, etc)
    units : str, optional
        Units that provided arguments should be interpreted as. This can be
        one of 'deg', 'degrees', 'rad', 'radians', 'meters', 'metres', and any
        parameter supported by the `cs2cs -lu <https://proj4.org/apps/cs2cs.html#cmdoption-cs2cs-lu>`_
        command. Units are determined in the following priority:

        1. units expressed with variables via @your_units (see 'Using units' under
           :ref:`Examples_of_wind_info.sh` for examples)
        2. units passed to ``--units`` (exluding center)
        3. meters (exluding center, which is degrees)

    area_extent : list, optional
        Area extent in projection units (lower_left_y, lower_left_x, upper_right_y, upper_right_x)
    shape : list, optional
        Number of pixels in the y and x direction following row-major format (height, width).
        Note that shape can be found from the displacement file or the area provided.
    center : list, optional
        Center of projection (lat, long)
    pixel_size : list or float, optional
        Size of pixels: (dy, dx)
    upper_left_extent : list, optional
        Projection y and x coordinates of the upper left corner of the upper left pixel (y, x)
    radius : list or float, optional
        Projection length from the center to the left/right and top/bottom outer edges (dy, dx)
    projection_ellipsoid : string or Geod, optional
        ellipsoid of projection (WGS84, sphere, etc)

        Returns
        -------
            area : dict
                projection, lat_0 (degrees), long_0 (degrees), equatorial radius (meters), eccentricity,
                inverse_flattening, shape, area_extent (degrees), pixel_size (projection meters), center (degrees)
    """
    if not isinstance(lat_0, (int, float)) or not isinstance(long_0, (int, float)):
        raise ValueError(
            'lat_0 and long_0 must be ints or floats, but instead were ' + '{0} {1} and {2} {3} respectively'.format(
                lat_0, type(lat_0), long_0, type(long_0)))
    return _find_displacements_and_area(lat_ts=lat_ts, lat_0=lat_0, long_0=long_0, displacement_data=displacement_data,
                                        projection=projection, area_extent=area_extent, shape=shape, center=center,
                                        pixel_size=pixel_size, upper_left_extent=upper_left_extent, radius=radius,
                                        units=units, projection_ellipsoid=projection_ellipsoid)[4]


def displacements(lat_ts=None, lat_0=None, long_0=None, displacement_data=None, projection=None, j=None, i=None,
                  area_extent=None, shape=None, center=None, pixel_size=None, upper_left_extent=None, radius=None,
                  units=None, projection_ellipsoid=None):
    """Dynamically computes displacements.

    Parameters
    ----------
    lat_ts: float, optional
        Latitude  of true scale
    lat_0 : float, optional
        Latitude of origin
    long_0 : float, optional
        Central meridian
    displacement_data : str or list, optional
        Filename or list containing displacements: [tag, width, height, i_11, j_11, i_12, j_12, ..., i_nm, j_nm] or
        [[j_displacement], [i_displacement]] respectively
    projection : str, optional
        Name of projection that pixels are describing (stere, laea, merc, etc).
    units : str, optional
        Units that provided arguments should be interpreted as. This can be
        one of 'deg', 'degrees', 'rad', 'radians', 'meters', 'metres', and any
        parameter supported by the `cs2cs -lu <https://proj4.org/apps/cs2cs.html#cmdoption-cs2cs-lu>`_
        command. Units are determined in the following priority:

        1. units expressed with variables via @your_units (see 'Using units' under
           :ref:`Examples_of_wind_info.sh` for examples)
        2. units passed to ``--units`` (exluding center)
        3. meters (exluding center, which is degrees)

    j : float or None, optional
        Row to run calculations on
    i : float or None, optional
        Column to run calculations on
    area_extent : list, optional
        Area extent in projection units [lower_left_y, lower_left_x, upper_right_y, upper_right_x]
    shape : list, optional
        Number of pixels in the y and x direction following row-major format (height, width).
        Note that shape can be found from the displacement file or the area provided.
    center : list, optional
        Center of projection (lat, long)
    pixel_size : list or float, optional
        Size of pixels: (dy, dx)
    upper_left_extent : list, optional
        Projection y and x coordinates of the upper left corner of the upper left pixel (y, x)
    radius : list or float, optional
        Projection length from the center to the left/right and top/bottom outer edges (dy, dx)
    projection_ellipsoid : string or Geod, optional
        ellipsoid of projection (WGS84, sphere, etc)

        Returns
        -------
            (j_displacements, i_displacements) : numpy.array or list
                j_displacements and i_displacements found in displacement file or list in row-major format
    """
    # Easier to treat as other functions.
    if displacement_data is None:
        raise ValueError('displacement_data is required to find displacements but was not provided or found.')
    shape, j_displacement, i_displacement = _find_displacements_and_area(lat_ts=lat_ts, lat_0=lat_0, long_0=long_0,
                                                                         displacement_data=displacement_data,
                                                                         projection=projection, j=j, i=i,
                                                                         area_extent=area_extent, shape=shape,
                                                                         center=center, pixel_size=pixel_size,
                                                                         upper_left_extent=upper_left_extent,
                                                                         radius=radius, units=units,
                                                                         projection_ellipsoid=projection_ellipsoid)[:3]
    return np.array((_reshape(j_displacement, shape), _reshape(i_displacement, shape)))


def velocity(lat_ts, lat_0, long_0, delta_time, displacement_data=None, projection=None, j=None, i=None,
             area_extent=None, shape=None, center=None, pixel_size=None, upper_left_extent=None, radius=None,
             units=None, projection_ellipsoid=None, earth_ellipsoid=None):
    """Computes the speed and angle of the wind given an area and pixel-displacement.

    Parameters
    ----------
    lat_ts: float
        Latitude  of true scale
    lat_0 : float
        Latitude of origin
    long_0 : float
        Central meridian
    delta_time : int
        Amount of time that separates both files in minutes.
    displacement_data : str or list, optional
        Filename or list containing displacements: [tag, width, height, i_11, j_11, i_12, j_12, ..., i_nm, j_nm] or
        [[j_displacement], [i_displacement]] respectively
    projection : str
        Name of projection that the image is in (stere, laea, merc, etc).
    units : str, optional
        Units that provided arguments should be interpreted as. This can be
        one of 'deg', 'degrees', 'rad', 'radians', 'meters', 'metres', and any
        parameter supported by the `cs2cs -lu <https://proj4.org/apps/cs2cs.html#cmdoption-cs2cs-lu>`_
        command. Units are determined in the following priority:

        1. units expressed with variables via @your_units (see 'Using units' under
           :ref:`Examples_of_wind_info.sh` for examples)
        2. units passed to ``--units`` (exluding center)
        3. meters (exluding center, which is degrees)

    j : float or None, optional
        Row to run calculations on
    i : float or None, optional
        Column to run calculations on
    area_extent : list, optional
        Area extent in projection units [lower_left_y, lower_left_x, upper_right_y, upper_right_x]
    shape : list, optional
        Number of pixels in the y and x direction following row-major format (height, width).
        Note that shape can be found from the displacement file or the area provided.
    center : list, optional
        Center of projection (lat, long)
    pixel_size : list or float, optional
        Size of pixels: (dy, dx)
    upper_left_extent : list, optional
        Projection y and x coordinates of the upper left corner of the upper left pixel (y, x)
    radius : list or float, optional
        Projection length from the center to the left/right and top/bottom outer edges (dy, dx)
    projection_ellipsoid : string or Geod, optional
        ellipsoid of projection (WGS84, sphere, etc)
    earth_ellipsoid : string or Geod, optional
        ellipsoid of Earth (WGS84, sphere, etc)

    Returns
    -------
        (speed, angle) : numpy.array or list
            speed and angle (measured clockwise from north) of the wind calculated
            from area and pixel-displacement in row-major format
    """
    shape, speed, angle = _compute_velocity(lat_ts, lat_0, long_0, delta_time, displacement_data=displacement_data,
                                            projection=projection, j=j, i=i, area_extent=area_extent, shape=shape,
                                            center=center, pixel_size=pixel_size, upper_left_extent=upper_left_extent,
                                            radius=radius, units=units, projection_ellipsoid=projection_ellipsoid,
                                            earth_ellipsoid=earth_ellipsoid)[:3]
    return np.array((_reshape(speed, shape), _reshape(angle, shape)))


def velocity_fll(delta_time, old_lat, old_long, new_lat, new_long, earth_ellipsoid=None):
    """Computes the speed and angle of the wind given two latitudes and longitudes.

    Parameters
    ----------
    delta_time : int
        Amount of time that separates both files in minutes.
    old_lat: float
        Starting point latitude
    old_long: float
        Starting point longitude
    new_lat: float
        Ending point latitude
    new_long: float
        Ending point longitude
    earth_ellipsoid: str, optional
        ellipsoid of Earth (WGS84, sphere, etc)

    Returns
    -------
        (speed, angle) : numpy.array or list
            speed and angle (measured clockwise from north) of the wind calculated
            from area and pixel-displacement in row-major format
    """

    return wind_info_fll(delta_time, old_lat, old_long, new_lat, new_long, earth_ellipsoid=earth_ellipsoid)[2:4]


def vu(lat_ts, lat_0, long_0, delta_time, displacement_data=None, projection=None, j=None, i=None, area_extent=None,
       shape=None, center=None, pixel_size=None, upper_left_extent=None, radius=None, units=None,
       projection_ellipsoid=None, earth_ellipsoid=None):
    """Computes the v and u components of the wind given an area and pixel-displacement.

    Parameters
    ----------
    lat_ts: float
        Latitude  of true scale
    lat_0 : float
        Latitude of origin
    long_0 : float
        Central meridian
    delta_time : int
        Amount of time that separates both files in minutes.
    displacement_data : str or list, optional
        Filename or list containing displacements: [tag, width, height, i_11, j_11, i_12, j_12, ..., i_nm, j_nm] or
        [[j_displacement], [i_displacement]] respectively
    projection : str
        Name of projection that pixels are describing (stere, laea, merc, etc).
    units : str, optional
        Units that provided arguments should be interpreted as. This can be
        one of 'deg', 'degrees', 'rad', 'radians', 'meters', 'metres', and any
        parameter supported by the `cs2cs -lu <https://proj4.org/apps/cs2cs.html#cmdoption-cs2cs-lu>`_
        command. Units are determined in the following priority:

        1. units expressed with variables via @your_units (see 'Using units' under
           :ref:`Examples_of_wind_info.sh` for examples)
        2. units passed to ``--units`` (exluding center)
        3. meters (exluding center, which is degrees)

    j : float or None, optional
        Row to run calculations on
    i : float or None, optional
        Column to run calculations on
    area_extent : list, optional
        Area extent in projection units [lower_left_y, lower_left_x, upper_right_y, upper_right_x]
    shape : list, optional
        Number of pixels in the y and x direction following row-major format (height, width).
        Note that shape can be found from the displacement file or the area provided.
    center : list, optional
        Center of projection (lat, long)
    pixel_size : list or float, optional
        Size of pixels: (dy, dx)
    upper_left_extent : list, optional
        Projection y and x coordinates of the upper left corner of the upper left pixel (y, x)
    radius : list or float, optional
        Projection length from the center to the left/right and top/bottom outer edges (dy, dx)
    projection_ellipsoid : string or Geod, optional
        ellipsoid of projection (WGS84, sphere, etc)
    earth_ellipsoid : string or Geod, optional
        ellipsoid of Earth (WGS84, sphere, etc)

    Returns
    -------
        (v, u) : numpy.array or list
            v and u components of wind calculated from area and pixel-displacement in row-major format
    """
    shape, v, u = _compute_vu(lat_ts, lat_0, long_0, delta_time, displacement_data=displacement_data,
                              projection=projection, j=j, i=i, area_extent=area_extent, shape=shape, center=center,
                              pixel_size=pixel_size, upper_left_extent=upper_left_extent, radius=radius, units=units,
                              projection_ellipsoid=projection_ellipsoid, earth_ellipsoid=earth_ellipsoid)[:3]
    return np.array((_reshape(v, shape), _reshape(u, shape)))


def vu_fll(delta_time, old_lat, old_long, new_lat, new_long, earth_ellipsoid=None):
    """Computes the v and u components of the wind given two latitudes and longitudes.

    Parameters
    ----------
    delta_time : int
        Amount of time that separates both files in minutes.
    old_lat: float
        Starting point latitude
    old_long: float
        Starting point longitude
    new_lat: float
        Ending point latitude
    new_long: float
        Ending point longitude
    earth_ellipsoid: str, optional
        ellipsoid of Earth (WGS84, sphere, etc)

    Returns
    -------
        (v, u) : numpy.array or list
            v and u components of wind calculated from area and pixel-displacement in row-major format
    """
    return wind_info_fll(delta_time, old_lat, old_long, new_lat, new_long, earth_ellipsoid=earth_ellipsoid)[4:]


def lat_long(lat_ts, lat_0, long_0, displacement_data=None, projection=None, j=None, i=None, area_extent=None,
             shape=None, center=None, pixel_size=None, upper_left_extent=None, radius=None, units=None,
             projection_ellipsoid=None):
    """Computes the latitude and longitude given an area and pixel-displacement.

    Parameters
    ----------
    lat_ts: float
        Latitude  of true scale
    lat_0 : float
        Latitude of origin
    long_0 : float
        Central meridian
    displacement_data : str or list, optional
        Filename or list containing displacements: [tag, width, height, i_11, j_11, i_12, j_12, ..., i_nm, j_nm] or
        [[j_displacement], [i_displacement]] respectively
    projection : str
        Name of projection that pixels are describing (stere, laea, merc, etc).
    units : str, optional
        Units that provided arguments should be interpreted as. This can be
        one of 'deg', 'degrees', 'rad', 'radians', 'meters', 'metres', and any
        parameter supported by the `cs2cs -lu <https://proj4.org/apps/cs2cs.html#cmdoption-cs2cs-lu>`_
        command. Units are determined in the following priority:

        1. units expressed with variables via @your_units (see 'Using units' under
           :ref:`Examples_of_wind_info.sh` for examples)
        2. units passed to ``--units`` (exluding center)
        3. meters (exluding center, which is degrees)

    j : float or None, optional
        Row to run calculations on
    i : float or None, optional
        Column to run calculations on
    area_extent : list, optional
        Area extent in projection units [lower_left_y, lower_left_x, upper_right_y, upper_right_x]
    shape : list, optional
        Number of pixels in the y and x direction following row-major format (height, width).
        Note that shape can be found from the displacement file or the area provided.
    center : list, optional
        Center of projection (lat, long)
    pixel_size : list or float, optional
        Size of pixels: (dy, dx)
    upper_left_extent : list, optional
        Projection y and x coordinates of the upper left corner of the upper left pixel (y, x)
    radius : list or float, optional
        Projection length from the center to the left/right and top/bottom outer edges (dy, dx)
    projection_ellipsoid : string or Geod, optional
        ellipsoid of projection (WGS84, sphere, etc)

    Returns
    -------
        (latitude, longitude) : numpy.array or list
            latitude and longitude calculated from area and pixel-displacement in row-major format
    """
    # If no displacements were given, then old=new
    shape, new_lat, new_long, old_lat, old_long = _compute_lat_long(lat_ts, lat_0, long_0,
                                                                    displacement_data=displacement_data,
                                                                    projection=projection, j=j, i=i,
                                                                    area_extent=area_extent, shape=shape, center=center,
                                                                    pixel_size=pixel_size,
                                                                    upper_left_extent=upper_left_extent, radius=radius,
                                                                    units=units,
                                                                    projection_ellipsoid=projection_ellipsoid)
    return np.array((_reshape(old_lat, shape), _reshape(old_long, shape)))


def loxodrome_bck(old_lat, old_long, new_lat, new_long, earth_ellipsoid=None):
    """Computes the distance, forward bearing and back bearing given a starting and ending position.

    Credit: https://search-proquest-com.ezproxy.library.wisc.edu/docview/2130848771?rfr_id=info%3Axri%2Fsid%3Aprimo

    Parameters
    ----------
    old_lat: float
        Starting point latitude
    old_long: float
        Starting point longitude
    new_lat: float
        Ending point latitude
    new_long: float
        Ending point longitude
    earth_ellipsoid: str, optional
        ellipsoid of Earth (WGS84, sphere, etc)

    Returns
    -------
    (distance, forward bearing, back bearing) : numpy.array or list
        distance, forward bearing, and back bearing from initial position to final position
    """
    geod_info = _make_ellipsoid(earth_ellipsoid, 'earth_ellipsoid')
    logger.debug('Earth ellipsoid data: {0}'.format(geod_info.initstring.replace('+', '')))
    # eccentricity squared.
    es = (2 - geod_info.f) * geod_info.f
    e = es ** .5
    # Note: atanh(sin(x)) == asinh(tan(x)) for -pi / 2 <= x <= pi / 2
    delta_longitude = _delta_longitude(new_long, old_long)
    forward_bearing = _arctan2(delta_longitude, _arctanh(_sin(new_lat)) - e * _arctanh(e * _sin(new_lat)) -
                               (_arctanh(_sin(old_lat)) - e * _arctanh(e * _sin(old_lat))))
    # If staying at a pole.
    forward_bearing = np.where(np.isnan(forward_bearing) == False, forward_bearing, new_lat + 90)
    meridian_dist = geod_info.inv(np.zeros(np.shape(old_lat)), old_lat, np.zeros(np.shape(old_lat)), new_lat)[-1]
    length = abs(meridian_dist / _cos(forward_bearing))
    lat_radius = geod_info.a / (1 - es * _sin(new_lat) ** 2) ** .5 * _cos(new_lat)
    # Only used when staying on the same latitude.
    horizontal_length = lat_radius * np.radians(abs(delta_longitude))
    # If staying on a lat, use horizontal_length. Unless at poles to prevent rounding error.
    length = np.where((new_lat != old_lat) | (abs(new_lat) == 90), length, horizontal_length)
    return length, forward_bearing % 360, (forward_bearing - 180) % 360


def loxodrome_fwd(old_lat, old_long, distance, forward_bearing, earth_ellipsoid=None):
    """Computes the new lat, new long, and back bearing given a starting position, distance, and forward bearing.

    Credit: https://search-proquest-com.ezproxy.library.wisc.edu/docview/2130848771?rfr_id=info%3Axri%2Fsid%3Aprimo

    Parameters
    ----------
    old_lat: float
        Starting point latitude
    old_long: float
        Starting point longitude
    distance: float
        Distance from old position to new position
    forward_bearing: float
        Forward bearing from old position to new position
    earth_ellipsoid: str, optional
        ellipsoid of Earth (WGS84, sphere, etc)

    Returns
    -------
    (new lat, new long, back bearing) : numpy.array or list
        new latitude, new longitude, and back bearing from initial position
    """
    geod_info = _make_ellipsoid(earth_ellipsoid, 'earth_ellipsoid')
    logger.debug('Earth ellipsoid data: {0}'.format(geod_info.initstring.replace('+', '')))
    # eccentricity squared.
    es = (2 - geod_info.f) * geod_info.f
    e = es ** .5
    new_lat = geod_info.fwd(np.zeros(np.shape(old_lat)), old_lat, np.zeros(np.shape(old_lat)),
                            _cos(forward_bearing) * distance)[1]
    new_long = _tan(forward_bearing) * (_arctanh(_sin(new_lat)) - e * _arctanh(e * _sin(new_lat)) -
                                        (_arctanh(_sin(old_lat)) - e * _arctanh(e * _sin(old_lat)))) + old_long
    new_long = _delta_longitude(new_long, 0)
    # Only used if new_lat == old_lat.
    lat_radius = geod_info.a / (1 - es * _sin(old_lat) ** 2) ** .5 * _cos(old_lat)
    # Makes it so that going east or west uses the correct formula. Note: tange(angle) -> 0 as angle -> 0; this
    # yields a nice convergence.
    new_long = np.where(((new_long != old_long) | (forward_bearing % 180 == 0)) & (forward_bearing % 180 != 90),
                        new_long, _delta_longitude(-np.sign(forward_bearing % 360 - 180) *
                                                   np.degrees(distance / lat_radius) + old_long, 0))
    return new_lat, new_long, (forward_bearing - 180) % 360


def geodesic_bck(old_lat, old_long, new_lat, new_long, earth_ellipsoid=None):
    """Computes the shortest distance, initial bearing and back bearing given a starting and ending position.

    Parameters
    ----------
    old_lat: float
        Starting point latitude
    old_long: float
        Starting point longitude
    new_lat: float
        Ending point latitude
    new_long: float
        Ending point longitude
    earth_ellipsoid: str, optional
        ellipsoid of Earth (WGS84, sphere, etc)

    Returns
    -------
    (distance, forward bearing, back bearing) : numpy.array or list
        distance, forward bearing, and back bearing from initial position to final position
    """
    geod_info = _make_ellipsoid(earth_ellipsoid, 'earth_ellipsoid')
    logger.debug('Earth ellipsoid data: {0}'.format(geod_info.initstring.replace('+', '')))
    initial_bearing, back_bearing, distance = geod_info.inv(old_long, old_lat, new_long, new_lat)
    return distance, initial_bearing % 360, back_bearing % 360


def geodesic_fwd(old_lat, old_long, distance, initial_bearing, earth_ellipsoid=None):
    """Computes the new lat, new long, and back bearing given a starting position, distance, and forward bearing.

    Parameters
    ----------
    old_lat: float
        Starting point latitude
    old_long: float
        Starting point longitude
    distance: float
        Distance from old position to new position
    initial_bearing: float
        Initial bearing from old position to new position
    earth_ellipsoid: str, optional
        ellipsoid of Earth (WGS84, sphere, etc)

    Returns
    -------
    (new lat, new long, back bearing) : numpy.array or list
        new latitude, new longitude, and back bearing from initial position
    """
    geod_info = _make_ellipsoid(earth_ellipsoid, 'earth_ellipsoid')
    logger.debug('Earth ellipsoid data: {0}'.format(geod_info.initstring.replace('+', '')))
    new_long, new_lat, back_bearing = geod_info.fwd(old_long, old_lat, initial_bearing, distance)
    return new_lat, new_long, back_bearing % 360


def position_to_pixel(lat_ts, lat_0, long_0, lat, long, projection=None, area_extent=None, shape=None, center=None,
                      pixel_size=None, upper_left_extent=None, radius=None, projection_ellipsoid=None, units=None,
                      displacement_data=None):
    """Calculates the pixel given a position

    Parameters
    ----------
    lat_ts: float
        Latitude  of true scale
    lat_0 : float
        Latitude of origin
    long_0 : float
        Central meridian
    displacement_data : str or list, optional
        Filename or list containing displacements: [tag, width, height, i_11, j_11, i_12, j_12, ..., i_nm, j_nm] or
        [[j_displacement], [i_displacement]] respectively
    projection : str
        Name of projection that pixels are describing (stere, laea, merc, etc).
    units : str, optional
        Units that provided arguments should be interpreted as. This can be
        one of 'deg', 'degrees', 'rad', 'radians', 'meters', 'metres', and any
        parameter supported by the `cs2cs -lu <https://proj4.org/apps/cs2cs.html#cmdoption-cs2cs-lu>`_
        command. Units are determined in the following priority:

        1. units expressed with variables via @your_units (see 'Using units' under
           :ref:`Examples_of_wind_info.sh` for examples)
        2. units passed to ``--units`` (exluding center)
        3. meters (exluding center, which is degrees)

    j : float or None, optional
        Row to run calculations on
    i : float or None, optional
        Column to run calculations on
    area_extent : list, optional
        Area extent in projection units [lower_left_y, lower_left_x, upper_right_y, upper_right_x]
    shape : list, optional
        Number of pixels in the y and x direction following row-major format (height, width).
        Note that shape can be found from the displacement file or the area provided.
    center : list, optional
        Center of projection (lat, long)
    pixel_size : list or float, optional
        Size of pixels: (dy, dx)
    upper_left_extent : list, optional
        Projection y and x coordinates of the upper left corner of the upper left pixel (y, x)
    radius : list or float, optional
        Projection length from the center to the left/right and top/bottom outer edges (dy, dx)
    projection_ellipsoid : string or Geod, optional
        ellipsoid of projection (WGS84, sphere, etc)

    Returns
    -------
    (j, i) : numpy.array or list
        j and i pixel that the provided latitude and longitude represent on the given area.
    """
    area_definition = _find_displacements_and_area(lat_ts=lat_ts, lat_0=lat_0, long_0=long_0, projection=projection,
                                                   area_extent=area_extent, shape=shape, center=center,
                                                   pixel_size=pixel_size, upper_left_extent=upper_left_extent,
                                                   radius=radius, projection_ellipsoid=projection_ellipsoid,
                                                   units=units, displacement_data=displacement_data)[3]
    u_l_pixel = area_definition.pixel_upper_left
    p = Proj(area_definition.proj_dict, errcheck=True, preserve_units=True)
    position = p(long, lat)
    i = (position[0] - u_l_pixel[0]) / area_definition.pixel_size_x
    j = (u_l_pixel[1] - position[1]) / area_definition.pixel_size_y
    return j, i


def wind_info(lat_ts, lat_0, long_0, delta_time, displacement_data=None, projection=None, j=None, i=None,
              area_extent=None, shape=None, center=None, pixel_size=None, upper_left_extent=None, radius=None,
              units=None, projection_ellipsoid=None, earth_ellipsoid=None, no_save=False, save_directory=None,
              timestamp=None):
    """Computes the latitude, longitude, velocity, angle, v, and u of the wind given an area and pixel-displacement.

    Parameters
    ----------
    lat_ts: float
        Latitude of true scale
    lat_0 : float
        Latitude of origin
    long_0 : float
        Central meridian
    delta_time : int
        Amount of time that separates both files in minutes.
    displacement_data : str or list, optional
        Filename or list containing displacements: [tag, width, height, i_11, j_11, i_12, j_12, ..., i_nm, j_nm] or
        [[j_displacement], [i_displacement]] respectively
    projection : str
        Name of projection that pixels are describing (stere, laea, merc, etc).
    units : str, optional
        Units that provided arguments should be interpreted as. This can be
        one of 'deg', 'degrees', 'rad', 'radians', 'meters', 'metres', and any
        parameter supported by the `cs2cs -lu <https://proj4.org/apps/cs2cs.html#cmdoption-cs2cs-lu>`_
        command. Units are determined in the following priority:

        1. units expressed with variables via @your_units (see 'Using units' under
           :ref:`Examples_of_wind_info.sh` for examples)
        2. units passed to ``--units`` (exluding center)
        3. meters (exluding center, which is degrees)

    j : float or None, optional
        Row to run calculations on
    i : float or None, optional
        Column to run calculations on
    area_extent : list, optional
        Area extent in projection units [lower_left_y, lower_left_x, upper_right_y, upper_right_x]
    shape : list, optional
        Number of pixels in the y and x direction following row-major format (height, width).
        Note that shape can be found from the displacement file or the area provided.
    center : list, optional
        Center of projection (lat, long)
    pixel_size : list or float, optional
        Size of pixels: (dy, dx)
    upper_left_extent : list, optional
        Projection y and x coordinates of the upper left corner of the upper left pixel (y, x)
    radius : list or float, optional
        Projection length from the center to the left/right and top/bottom outer edges (dy, dx)
    projection_ellipsoid : string or Geod, optional
        ellipsoid of projection (WGS84, sphere, etc)
    earth_ellipsoid : string or Geod, optional
        ellipsoid of Earth (WGS84, sphere, etc)
    no_save : bool, optional
        When False, saves wind_info to name_of_projection.txt, j_displacement.txt, i_displacement.txt,
        new_latitude.txt, new_longitude.txt, old_latitude.txt, old_longitude.txt, v.txt, u.txt, speed.txt, angle.txt,
        and wind_info.txt in that order (name_of_projection varies depending on the type of projection). Each of these
        variables are saved to wind_info.nc by the same name as their .txt counterparts in a new directory
        provided by the save_directory argument.
    save_directory: str, optional
        Directory in which to save the file containing data (also a directory) to. If the directory provided
        does not exist, then it is created. Defaults to a new directory by the name of the displacement file
        read appended with "_output_YYYYmmdd_HHMMSS" (the date and time when the script was ran), created
        where the script is ran
    timestamp: str, optional
        The time at which the script was ran. Defaults to the current time in not provided.

    Returns
    -------
        (latitude, longitude, velocity, angle, v, and u at each pixel) : numpy.array or list
            [latitude, longitude, velocity, angle, v, u] at each pixel in row-major format
    """
    if no_save is True and save_directory is not None:
        logger.warning('Conflicting options: --print and --save_directory. Listening to --print')
    # Only lets wind_info save to make life easier.
    if no_save is False:
        # Get name of displacement file (without path). If string is not a file, return and don't make a file.
        if isinstance(displacement_data, str):
            head, tail = ntpath.split(displacement_data)
            extension = tail or ntpath.basename(head)
        else:
            extension = 'list'
        # If no save directory was given, make save directory where script was ran.
        directory = save_directory if isinstance(save_directory, str) else os.getcwd()
        directory = os.path.join(directory, extension + '_output')
        if timestamp is None:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        save_directory = directory + '_' + timestamp
        if extension != 'list' and (displacement_data is None or not os.path.exists(displacement_data)):
            logger.warning(
                'Save directory {0} not created: displacement_data not found or provided'.format(save_directory))
        else:
            logger.debug('Creating save file')
            # Creates the save directory and the wind_info.nc file.
            _save_data(save_directory, [], mode='w')
    shape, v, u, speed, angle, lat, long = _compute_vu(lat_ts, lat_0, long_0, displacement_data=displacement_data,
                                                       projection=projection, j=j, i=i, delta_time=delta_time,
                                                       area_extent=area_extent, shape=shape, center=center,
                                                       pixel_size=pixel_size, upper_left_extent=upper_left_extent,
                                                       radius=radius, units=units,
                                                       projection_ellipsoid=projection_ellipsoid,
                                                       earth_ellipsoid=earth_ellipsoid, no_save=no_save,
                                                       save_directory=save_directory)
    logger.debug('Formatting wind_info')
    # Make each variable its own column.
    winds = np.insert(np.expand_dims(np.ravel(lat), axis=1), 1, long, axis=1)
    winds = np.insert(winds, 2, speed, axis=1)
    winds = np.insert(winds, 3, angle, axis=1)
    winds = np.insert(winds, 4, v, axis=1)
    winds = np.insert(winds, 5, u, axis=1)
    # Reshapes so that when one pixel is specified, each variable is its own row instead of its own column.
    if np.shape(winds)[0] == 1:
        winds = winds[0]
        text_shape = [1, 6]
        dims = ['vars']
    else:
        text_shape = None
        dims = ['yx', 'vars']
    if no_save is False:
        logger.debug('Saving wind_info')
        # Creates the file or writes over old data.
        _save_data(save_directory, [xarray.DataArray(winds, name='wind_info', dims=dims,
                                                     attrs={'standard_name': 'wind_speed',
                                                            'description': 'new_lat, new_long, speed, angle, v, u',
                                                            'grid_mapping_name': 'polar_stereographic'})],
                   text_shape=text_shape)
    # Columns: lat, long, speed, direction, v, u
    return winds


def wind_info_fll(delta_time, old_lat, old_long, new_lat, new_long, earth_ellipsoid=None):
    """Computes the latitude, longitude, velocity, angle, v, and u of the wind given two latitudes and longitudes.

    Parameters
    ----------
    delta_time : int
        Amount of time that separates both files in minutes.
    old_lat: float
        Starting point latitude
    old_long: float
        Starting point longitude
    new_lat: float
        Ending point latitude
    new_long: float
        Ending point longitude
    earth_ellipsoid: str, optional
        ellipsoid of Earth (WGS84, sphere, etc)

    Returns
    -------
        (latitude, longitude, velocity, angle, v, and u at each pixel) : numpy.array or list
            [latitude, longitude, velocity, angle, v, u] at each pixel in row-major format
    """
    distance, angle = loxodrome_bck(old_lat, old_long, new_lat, new_long, earth_ellipsoid=earth_ellipsoid)[:2]
    speed = distance / (delta_time * 60)
    # IMPORTANT, THIS IS CORRECT: Since angle is measured counter-cloclwise from north, then v = sin(pi - angle) and
    # u = cos(pi - angle). sin(pi - angle) = cos(angle) and cos(pi - angle) = sin(angle)!
    v = _cos(angle) * speed
    u = _sin(angle) * speed
    # Make each variable its own column.
    winds = np.insert(np.expand_dims(np.ravel(new_lat), axis=1), 1, new_long, axis=1)
    winds = np.insert(winds, 2, speed, axis=1)
    winds = np.insert(winds, 3, angle, axis=1)
    winds = np.insert(winds, 4, v, axis=1)
    winds = np.insert(winds, 5, u, axis=1)
    # Reshapes so that when one pixel is specified, each variable is its own row instead of its own column.
    if np.shape(winds)[0] == 1:
        winds = winds[0]
    return winds
