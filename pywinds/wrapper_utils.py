import argparse
import ast
import os
import re
import sys
import traceback
import xarray
from glob import glob
from inspect import getfullargspec

import numpy as np


def area_to_string(area_dict):
    """Rounds and converts area dict to string"""
    def _round(val, precision):
        try:
            if np.shape(val) == ():
                return str(round(val, precision))
            return str(list(np.round(val, precision).tolist()))
        except (AttributeError, TypeError):
            return str(val)

    write_string = ''
    for key, val in area_dict.items():
        precision = 2
        if key == 'eccentricity' or key == 'flattening':
            precision = 6
        val = _round(val, precision)
        write_string = write_string + str(key) + ': ' + val + '\n'
    return write_string


def _num_and_units(var):
    print(var)
    match = re.match("([0-9]+)([a-z]+)", var, re.I)
    if match:
        val, units = match.groups()
        return _nums_or_string(val), units
    match = re.match("([0-9]+)(\.)([a-z]+)", var, re.I)
    if match:
        num, period, units = match.groups()
        return _nums_or_string(num + period), units
    match = re.match("([0-9]+)(\.)([0-9]+)([a-z]+)", var, re.I)
    if match:
        num, period, decimals, units = match.groups()
        return _nums_or_string(num + period + decimals), units
    return _nums_or_string(var)


def _nums_or_string(var):
    try:
        return ast.literal_eval('%s' % var)
    except ValueError:
        return var


class MyParser(argparse.ArgumentParser):
    """Used to control error placement a little better."""
    def error(self, message):
        print('error: %s\n' % message)
        self.print_help()
        sys.exit(2)


class UnitHandler(argparse.Action):
    def __call__(self, parser, args, values, option_string=None):
        # values = [_num_and_units(value) for value in values]
        units = None
        if np.shape(values[0]) == (2,) and np.shape(values[1]) == (2,):
            if values[0][1] == values[1][1]:
                units = values[0][1]
                values = values[0][0], values[1][0]
            else:
                print('center has wrong unit format\n')
                parser.parse_args(['-h'])
        elif np.shape(values[0]) != np.shape(values[1]):
            print('center has wrong unit format\n')
            parser.parse_args(['-h'])
        if units is not None:
            values = xarray.DataArray(values, attrs={'units': units})
        setattr(args, self.dest, values)


# TODO: FIX NEGATIVE NUMBERS WITH UNITS.
def _get_args(name):
    """Reads command line arguments and handles logic behind them."""
    arg_names = ['lat_ts', 'lat_0', 'long_0', 'delta_time']
    kwarg_names = ['center', 'pixel_size', 'units', 'shape', 'upper_left_extent', 'radius', 'area_extent',
                   'displacement_data', 'j', 'i', 'no_save', 'projection', 'projection_spheroid', 'earth_spheroid']
    parser = MyParser(description='', allow_abbrev=False)
    parser.add_argument('lat_ts', type=float, help='')
    parser.add_argument('lat_0', type=float, help='')
    parser.add_argument('long_0', type=float, help='')
    if name not in ['area', 'lat_long']:
        parser.add_argument('delta_time', type=float, help='')
    else:
        arg_names.remove('delta_time')
    parser.add_argument('--center', nargs=2, type=_num_and_units, action=UnitHandler, help='center of projection: '
                                                                                          'lat<units> '
                                                                          'long<units>')
    parser.add_argument('--pixel_size', nargs=2, type=_num_and_units, action=UnitHandler, help='size of pixels: '
                                                                                               'dy<units> dx<units>')
    parser.add_argument('--units', default='m',
                        help='units that provided arguments that take units (except center) should be interpreted as')
    parser.add_argument('--shape', type=_nums_or_string, nargs=2,
                        help='number of pixels in the y and x direction: height width')
    parser.add_argument('--upper_left_extent', nargs=2, type=_num_and_units, action=UnitHandler,
                        help='projection y and x coordinates of the upper left'
                             'corner of the upper left pixel: y<units> x<units>')
    parser.add_argument('--radius', nargs=2, type=_num_and_units, action=UnitHandler,
                        help='projection length from the center to the left/right'
                             'and top/bottom outer edges: dy<units> dx<units>')
    parser.add_argument('--area_extent', nargs=4, type=_num_and_units, action=UnitHandler,
                        help='area extent as a list: y_ll<units> x_ll<units> y_ur<units> x_ur<units>')
    parser.add_argument('--displacement_data', type=_nums_or_string, help='filename or list containing displacements')
    if name != 'area':
        parser.add_argument('--j', type=int, help='row to run calculations on')
        parser.add_argument('--i', type=int, help='column to run calculations on')
    else:
        kwarg_names.remove('j')
        kwarg_names.remove('i')
    if name == 'wind_info':
        parser.add_argument('--no_save', action="store_true", help="print data to shell without saving")
    else:
        kwarg_names.remove('no_save')
    parser.add_argument('--projection', default='stere', help='name of projection that the image is in')
    parser.add_argument('--projection_spheroid', default='WGS84', help='spheroid of projection')
    if name not in ['area', 'lat_long']:
        parser.add_argument('--earth_spheroid', default='WGS84', help='spheroid of Earth')
    else:
        kwarg_names.remove('earth_spheroid')

    commands = parser.parse_args()
    args = [getattr(commands, arg) for arg in arg_names]
    kwargs = {kwarg: getattr(commands, kwarg) for kwarg in kwarg_names}
    return args, kwargs, parser


def run_script(func, output_format, name, is_area=False, is_lat_long=False):
    """Runs python function from wind_functions.py."""
    args, kwargs, parser = _get_args(name)
    try:
        displacement_data = kwargs.get('displacement_data')
        if displacement_data is None and is_lat_long is False:
            displacement_data = os.path.join(os.getcwd(), '*.flo')
            kwargs['displacement_data'] = displacement_data
        if isinstance(displacement_data, str):
            files = glob(displacement_data)
            if files:
                for file in files:
                    kwargs['displacement_data'] = file
                    output = output_format(func(*args, **kwargs), kwargs)
                    if output is not '':
                        if len(files) > 1:
                            print('Reading displacements from:', file)
                        print(output)
                return
            # File not found error will be raised
            elif is_area is False:
                output = func(*args, **kwargs)
                print(output_format(output, kwargs))
            kwargs.pop('displacement_data')
        output = func(*args, **kwargs)
        print(output_format(output, kwargs))
    except Exception:
        print(traceback.format_exc())
        parser.parse_args(['-h'])
