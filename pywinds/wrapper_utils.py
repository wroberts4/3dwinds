import argparse
import ast
import logging
import os
import sys
from glob import glob

import xarray


logger = logging.getLogger(__name__)


def area_to_string(area_dict):
    """Rounds and converts area dict to string"""
    write_string = ''
    for key, val in area_dict.items():
        write_string = write_string + str(key) + ': ' + str(val) + '\n'
    return write_string


def _nums_or_string(var):
    """Converts strings to number like python objects"""
    try:
        return ast.literal_eval('%s' % var)
    except (ValueError, SyntaxError):
        return var


class NullParser(argparse.ArgumentParser):
    """Used to nullify error output."""
    def error(self, message):
        return


class MyFormatter(argparse.HelpFormatter):
    """Dynamically formats help message to be more informative."""
    def format_help(self):
        help = super(MyFormatter, self).format_help()
        formatter = ('{0} {0} {0} {0} {0}', '{0} {0} {0} {0}', '{0} {0} {0}', '{0} {0}', '{0}')
        for form in formatter:
            help = help.replace(form.format('UPPER_LEFT_EXTENT'), 'y x [units]')
            help = help.replace(form.format('RADIUS'), 'dy dx [units]')
            help = help.replace(form.format('AREA_EXTENT'), 'y_ll x_ll y_ur x_ur [units]')
            help = help.replace(form.format('CENTER'), 'y x [units]')
            help = help.replace(form.format('PIXEL_SIZE'), 'dy [dx] [units]')
        return help


class CustomAction(argparse.Action):
    """Dynamically finds correct number of nargs to use, then converts those numbers to correct python objects."""
    def __init__(self, option_strings, dest, narg_types=None, type=None, help=None):
        narg_types.sort(key=len)
        # If an error occurs or number of args are too small, use the bare minimum nargs.
        default_nargs = len(narg_types[0])
        # Setup narg_types so that larger lists take priority.
        narg_types = list(reversed(narg_types))
        # Setup parser to read all arguments after option.
        parser = NullParser()
        # Find the most amount of nargs possible.
        parser.add_argument(option_strings[0], nargs='*')
        # Setup argv to remove help flags and let main parser handle help.
        argv = sys.argv[1:]
        while '-h' in argv:
            argv.remove('-h')
        while '--help' in argv:
            argv.remove('--help')
        known_args = parser.parse_known_args(argv)
        # Extract only arguments associated with option.
        if known_args is not None:
            args = getattr(known_args[0], dest)
            if args is None:
                super().__init__(option_strings, dest, nargs=default_nargs, help=help)
                return
            args = [type(arg) for arg in args]
        else:
            super().__init__(option_strings, dest, nargs=default_nargs, help=help)
            return
        # Try to match up narg_types with args from command line.
        for narg_type in narg_types:
            if len(narg_type) <= len(args):
                for i in range(len(narg_type)):
                    if not isinstance(args[i], narg_type[i]):
                        break
                # Every type matched up:
                else:
                    super().__init__(option_strings, dest, nargs=len(narg_type), help=help)
                    return
        super().__init__(option_strings, dest, nargs=default_nargs, help=help)

    def __call__(self, parser, args, values, option_string=None):
        # Handles units.
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
    arg_names = ['lat-ts', 'lat-0', 'long-0']
    kwarg_names = ['center', 'pixel_size', 'units', 'shape', 'upper_left_extent', 'radius', 'area_extent',
                   'displacement_data', 'j', 'i', 'no_save', 'projection', 'projection_spheroid', 'earth_spheroid']
    my_parser = argparse.ArgumentParser(description='', formatter_class=MyFormatter)

    if name != 'displacements':
        my_parser.add_argument('lat-ts', type=float, help='projection latitude of true scale')
        my_parser.add_argument('lat-0', type=float, help='projection latitude of origin')
        my_parser.add_argument('long-0', type=float, help='projection central meridian')
    else:
        arg_names = []
    if name in ['wind_info', 'velocity', 'vu']:
        my_parser.add_argument('delta-time', type=float, help='amount of time that separates both files in minutes')
        arg_names.append('delta-time')
    my_parser.add_argument('--center', action=CustomAction, type=_nums_or_string,
                           narg_types=[[(float, int), (float, int), str], [(float, int), (float, int)]],
                           help='projection y and x coordinate of the center of area. Default: lat long')
    my_parser.add_argument('--pixel-size', action=CustomAction, type=_nums_or_string,
                           narg_types=[[(float, int), (float, int), str], [(float, int), (float, int)],
                                       [(float, int), str], [(float, int)]],
                           help='projection size of pixels in the y and x direction.'
                                'If pixels are square, i.e. dy = dx, then only one value needs to be entered')
    my_parser.add_argument('--displacement-data', type=_nums_or_string, metavar='filename',
                           help='filename or list containing displacements')
    if name != 'area':
        my_parser.add_argument('--j', type=int, metavar='int', help='row to run calculations on')
        my_parser.add_argument('--i', type=int, metavar='int', help='column to run calculations on')
    if name == 'wind_info':
        my_parser.add_argument('--no-save', action="store_true", help="print data to shell without saving")
    my_parser.add_argument('--units', metavar='str', help='units that all provided arguments that take units '
                                                          '(except center) should be interpreted as')
    my_parser.add_argument('--upper-left-extent', action=CustomAction, type=_nums_or_string,
                           narg_types=[[(float, int), (float, int), str], [(float, int), (float, int)]],
                           help='projection y and x coordinates of the upper left corner of the upper left pixel')
    my_parser.add_argument('--radius', action=CustomAction, type=_nums_or_string,
                           narg_types=[[(float, int), (float, int), str], [(float, int), (float, int)]],
                           help='projection length from the center to the left/rightand top/bottom outer edges')
    my_parser.add_argument('--area-extent', action=CustomAction, type=_nums_or_string,
                           narg_types=[[(float, int) for i in range(4)] + [str], [(float, int) for i in range(4)]],
                           help='area extent in projection space: lower_left_y,'
                                'lower_left_x, upper_right_y, upper_right_x')
    my_parser.add_argument('--shape', type=_nums_or_string, nargs=2, metavar=('height', 'width'),
                           help='number of pixels in the y and x direction')
    my_parser.add_argument('--projection', metavar='str', help='name of projection that the image is in')
    my_parser.add_argument('--projection-spheroid', metavar='str', help='spheroid of projection')
    if name in ['wind_info', 'velocity', 'vu']:
        my_parser.add_argument('--earth-spheroid', metavar='str', help='spheroid of Earth')
    my_parser.add_argument('-v', '--verbose', action="count", default=0,
                           help='each occurrence increases verbosity 1 level through ERROR-WARNING-INFO-DEBUG')
    commands = my_parser.parse_args()
    # Logging setup.
    levels = [logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG]
    logging_format = '[%(levelname)s: %(asctime)s : %(name)s] %(message)s'
    logging.basicConfig(level=levels[min(3, commands.verbose)], format=logging_format, datefmt='%Y-%m-%d %H:%M:%S')
    # Gets args and kwargs from command line data.
    args = [getattr(commands, arg) for arg in arg_names]
    kwargs = {}
    for name in kwarg_names:
        val = getattr(commands, name, None)
        if val is not None:
            kwargs[name] = val
    return args, kwargs, my_parser


def run_script(func, output_format, name, is_area=False, is_lat_long=False):
    """Runs python function from wind_functions.py."""
    args, kwargs, parser = _get_args(name)
    displacement_data = kwargs.get('displacement_data')
    if displacement_data is None and is_lat_long is False:
        displacement_data = os.path.join(os.getcwd(), '*.flo')
        kwargs['displacement_data'] = displacement_data
    if isinstance(displacement_data, str):
        files = glob(displacement_data)
        if files:
            for file in files:
                kwargs['displacement_data'] = os.path.abspath(file)
                output = output_format(func(*args, **kwargs), kwargs)
                if output is not '':
                    print(output)
            return
        # File not found error will be raised from trying to find *.flo.
        elif is_area is False:
            func(*args, **kwargs)
        kwargs.pop('displacement_data')
    output = func(*args, **kwargs)
    print(output_format(output, kwargs))
