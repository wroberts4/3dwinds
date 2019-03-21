import sys

import argparse
import ast
import numpy as np
import os
import traceback
import xarray
from glob import glob


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


def _nums_or_string(var):
    try:
        return ast.literal_eval('%s' % var)
    except (ValueError, SyntaxError):
        return var


class ErrorParser(argparse.ArgumentParser):
    """Used to control error placement a little better."""

    def error(self, message):
        print(message)
        self.print_help()
        sys.exit(2)


class NargsParser(argparse.ArgumentParser):
    """Used to control error placement a little better."""

    def error(self, message):
        return


class UnitHandler(argparse.Action):
    def __call__(self, parser, args, values, option_string=None):
        values = [_nums_or_string(value) for value in values]
        units = None
        if isinstance(values[-1], str):
            units = values.pop(-1)
        if len(values) == 1:
            values = values[0]
        if units is not None:
            values = xarray.DataArray(values, attrs={'units': units})
        setattr(args, self.dest, values)


def _get_args(name):
    """Reads command line arguments and handles logic behind them."""
    arg_names = ['lat_ts', 'lat_0', 'long_0', 'delta_time']
    kwarg_names = ['center', 'pixel_size', 'units', 'shape', 'upper_left_extent', 'radius', 'area_extent',
                   'displacement_data', 'j', 'i', 'no_save', 'projection', 'projection_spheroid', 'earth_spheroid']
    my_parser = ErrorParser(description='', allow_abbrev=False, conflict_handler='resolve')

    my_parser.add_argument('lat_ts', type=float, help='projection latitude of true scale')
    my_parser.add_argument('lat_0', type=float, help='projection latitude of origin')
    my_parser.add_argument('long_0', type=float, help='projection central meridian')
    if name not in ['area', 'lat_long']:
        my_parser.add_argument('delta_time', type=float, help='amount of time that separates both files in minutes')
    else:
        arg_names.remove('delta_time')
    my_parser.add_argument('--units', default='m', metavar='str',
                           help='units that all provided arguments that take units '
                                '(except center) should be interpreted as')
    my_parser.add_argument('--shape', type=_nums_or_string, nargs=2, metavar=('height', 'width'),
                           help='number of pixels in the y and x direction: height width')
    my_parser.add_argument('--displacement_data', type=_nums_or_string, metavar=('filename'),
                           help='filename or list containing displacements')
    if name != 'area':
        my_parser.add_argument('--j', type=int, metavar='int', help='row to run calculations on')
        my_parser.add_argument('--i', type=int, metavar='int', help='column to run calculations on')
    else:
        kwarg_names.remove('j')
        kwarg_names.remove('i')
    if name == 'wind_info':
        my_parser.add_argument('--no_save', action="store_true", help="print data to shell without saving")
    else:
        kwarg_names.remove('no_save')
    my_parser.add_argument('--projection', default='stere', metavar='str',
                           help='name of projection that the image is in')
    my_parser.add_argument('--projection_spheroid', metavar='str', default='WGS84', help='spheroid of projection')
    if name not in ['area', 'lat_long']:
        my_parser.add_argument('--earth_spheroid', metavar='str', default='WGS84', help='spheroid of Earth')
    else:
        kwarg_names.remove('earth_spheroid')
    my_parser = ErrorParser(description='', allow_abbrev=False, conflict_handler='resolve')
    # Used to transfer help on to my_parser.
    help_parser = ErrorParser(parents=[my_parser], conflict_handler='resolve')
    # Used to dynamically get nargs for my_parser.
    nargs_parser = NargsParser(parents=[my_parser], conflict_handler='resolve')

    nargs_parser.add_argument('--upper_left_extent', type=_nums_or_string, nargs='*')
    nargs_parser.add_argument('--radius', type=_nums_or_string, nargs='*')
    nargs_parser.add_argument('--area_extent', type=_nums_or_string, nargs='*')
    nargs_parser.add_argument('--center', type=_nums_or_string, nargs='*')
    nargs_parser.add_argument('--pixel_size', type=_nums_or_string, nargs='*')
    arg_list = nargs_parser.parse_args()
    nargs = {}
    for name in ['upper_left_extent', 'radius', 'area_extent', 'center', 'pixel_size']:
        attr = getattr(arg_list, name)
        if attr is None:
            nargs[name] = 3
        elif name == 'pixel_size' and len(attr) < 2:
            nargs[name] = 1
        elif len(attr) == 2 or not isinstance(attr[2], str):
            nargs[name] = 2
        else:
            nargs[name] = 3

    help_parser.add_argument('--upper_left_extent', nargs=3, metavar=('y', 'x', '[units]'),
                             help='projection y and x coordinates of the upper left '
                                  'corner of the upper left pixel: y<units> x<units>')
    help_parser.add_argument('--radius', nargs=3, metavar=('dy', 'dx', '[units]'),
                             help='projection length from the center to the left/right'
                                  'and top/bottom outer edges')
    help_parser.add_argument('--area_extent', nargs=5, metavar=('y_ll', 'x_ll', 'y_ur', 'x_ur', '[units]'),
                             help='area extent as a list')
    help_parser.add_argument('--center', nargs=3, metavar=('lat', 'long', '[units]'), help='center of projection')
    help_parser.add_argument('--pixel_size', nargs=3, metavar=('dy', '[dx]', '[units]'), help='size of pixels')

    my_parser.add_argument('--upper_left_extent', nargs=nargs['upper_left_extent'], action=UnitHandler)
    my_parser.add_argument('--radius', nargs=nargs['radius'], action=UnitHandler)
    my_parser.add_argument('--area_extent', nargs=nargs['area_extent'], action=UnitHandler)
    my_parser.add_argument('--center', nargs=nargs['center'], action=UnitHandler)
    my_parser.add_argument('--pixel_size', nargs=nargs['pixel_size'], action=UnitHandler)

    my_parser.print_help = help_parser.print_help

    commands = my_parser.parse_args()
    args = [getattr(commands, arg) for arg in arg_names]
    kwargs = {kwarg: getattr(commands, kwarg) for kwarg in kwarg_names}
    return args, kwargs, my_parser


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
