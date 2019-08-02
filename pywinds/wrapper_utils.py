"""Convert command line arguments to python arguments for wind_functions.py"""
import argparse
import ast
import copy
import datetime
import logging
import numpy as np
import os
from glob import glob

import xarray

logger = logging.getLogger(__name__)


def area_to_string(area_dict, round_nums=None):
    """Rounds and converts area dict to string"""
    write_string = ''
    for key, val in area_dict.items():
        if val is not None and not isinstance(val, str) and isinstance(round_nums, int):
            val = np.round(val, round_nums).tolist()
        write_string = write_string + str(key) + ': ' + str(val) + '\n'
    return write_string[:-1]


def _nums_or_string(var):
    """Converts strings to number like python objects, and leaves as default type if unable to convert."""
    try:
        return ast.literal_eval('%s' % var)
    except (ValueError, SyntaxError):
        return var


class NullParser(argparse.ArgumentParser):
    """Used to nullify error output."""

    def print_usage(self, *args, **kwargs):
        return

    def print_help(self, *args, **kwargs):
        return

    def exit(self, *args, **kwargs):
        return


class MyFormatter(argparse.HelpFormatter):
    """Dynamically formats help message to be more informative."""

    def format_help(self):
        help_string = super(MyFormatter, self).format_help()
        formatter = ('{0} {0} {0} {0} {0}', '{0} {0} {0} {0}', '{0} {0} {0}', '{0} {0}', '{0}')
        for form in formatter:
            help_string = help_string.replace(form.format('UPPER_LEFT_EXTENT'), 'y x [units]')
            help_string = help_string.replace(form.format('RADIUS'), 'dy [dx] [units]')
            help_string = help_string.replace(form.format('AREA_EXTENT'), 'y_ll x_ll y_ur x_ur [units]')
            help_string = help_string.replace(form.format('CENTER'), 'y x [units]')
            help_string = help_string.replace(form.format('SHAPE'), 'height width')
            help_string = help_string.replace(form.format('PIXEL_SIZE'), 'dy [dx] [units]')
            help_string = help_string.replace(form.format('EARTH_ELLIPSOID'), 'str [val [units]] [str val [units]]')
            help_string = help_string.replace(form.format('PROJECTION_ELLIPSOID'),
                                              'str [val [units]] [str val [units]]')
        return help_string


class DualParser(argparse.ArgumentParser):
    """Adds a null parser so that --help works for CustomAction"""

    def __init__(self, *args, **kwargs):
        data_type = kwargs.get('type') if kwargs.get('type') else _nums_or_string
        self.null_parser = NullParser(*args, conflict_handler='resolve', **kwargs)
        super().__init__(*args, **kwargs)

    def add_argument(self, *args, **kwargs):
        narg_types = kwargs.pop('narg_types', None)
        self.null_parser.add_argument(*args, **kwargs)
        if kwargs.get('action') is None:
            kwargs['action'] = CustomAction
            kwargs['parser'] = self.null_parser
            kwargs['narg_types'] = narg_types
        super().add_argument(*args, **kwargs)


class CustomAction(argparse.Action):
    """Dynamically finds correct number of nargs to use, then converts those numbers to correct python objects."""

    def __init__(self, option_strings, dest, narg_types=None, parser=None, **kwargs):
        if kwargs.get('nargs'):
            super().__init__(option_strings, dest, **kwargs)
            return
        type = kwargs if kwargs.get('type') else _nums_or_string
        narg_types = narg_types if narg_types else [[type]]
        narg_types.sort(key=len)
        # If an error occurs or number of args are too small, use the bare minimum nargs.
        default_nargs = len(narg_types[0])
        # Setup narg_types so that larger lists take priority.
        narg_types = list(reversed(narg_types))
        # Setup parser to read all arguments after option.
        parser = copy.deepcopy(parser)
        # Find the most amount of nargs possible.
        parser.add_argument(*option_strings if option_strings else [dest], nargs='+')
        # Setup argv to remove help flags and let main parser handle help.
        known_args = parser.parse_known_args()
        # Extract only arguments associated with option.
        if known_args is not None:
            args = getattr(known_args[0], dest)
            if not args:
                super().__init__(option_strings, dest, nargs=default_nargs, **kwargs)
                return
            args = [type(arg) for arg in args]
        else:
            super().__init__(option_strings, dest, nargs=default_nargs, **kwargs)
            return
        # Try to match up narg_types with args from command line.
        for narg_type in narg_types:
            if len(narg_type) <= len(args):
                for i in range(len(narg_type)):
                    narg_type[i] = (int, float) if narg_type[i] == float else narg_type[i]
                    narg_type[i] = (int, float, str) if narg_type[i] == _nums_or_string else narg_type[i]
                    if not isinstance(args[i], narg_type[i]):
                        break
                # Every type matched up:
                else:
                    super().__init__(option_strings, dest, nargs=len(narg_type), **kwargs)
                    return
        super().__init__(option_strings, dest, nargs=default_nargs, **kwargs)

    def __call__(self, parser, args, values, option_string=None):
        values = [_nums_or_string(value) for value in values]
        if option_string and ('ellipsoid' in option_string or 'spheroid' in option_string):
            if len(values) == 3:
                values = {values[0]: xarray.DataArray(values[1], attrs={'units': values[2]})}
            elif len(values) == 5:
                if isinstance(values[3], (int, float)):
                    values = {values[0]: values[1],
                              values[2]: xarray.DataArray(values[3], attrs={'units': values[4]})}
                else:
                    values = {values[0]: xarray.DataArray(values[1], attrs={'units': values[2]}),
                              values[3]: values[4]}
            elif len(values) == 6:
                values = {key: xarray.DataArray(val, attrs={'units': units}) for key, val, units in
                          zip(values[::3], values[-5::3], values[-4::3])}
            elif len(values) != 1:
                values = {key: val for key, val in zip(values[::2], values[1::2])}
        else:
            if len(values) == 1:
                values = values[0]
            else:
                units = None
                if isinstance(values[-1], str):
                    units = values.pop(-1)
                    if len(values) == 1:
                        values = values[0]
                if units is not None:
                    values = xarray.DataArray(values, attrs={'units': units})
        if isinstance(values, list) and len(values) == 1:
            values = values[0]
        setattr(args, self.dest, values)


def _add_flag(dictionary, *names, **kwargs):
    dictionary.update(dict.fromkeys(names, dict(args=names, kwargs=kwargs)))


def _make_parser(flag_names, description):
    # Adds flags that are for every script.
    flag_names = ['-v'] + flag_names + ['--precision']
    my_parser = DualParser(description=description, formatter_class=MyFormatter)
    flags = {}
    _add_flag(flags, '-v', '--verbose', action="count", default=0,
              help='Each occurrence increases verbosity 1 level through ERROR-WARNING-INFO-DEBUG.')
    _add_flag(flags, 'old-lat', help='Latitude of starting location.')
    _add_flag(flags, 'old-long', help='Longitude of starting locaion.')
    _add_flag(flags, 'new-lat', help='Latitude of ending location')
    _add_flag(flags, 'new-long', help='Longitude of ending location')
    _add_flag(flags, 'distance', narg_types=[[float], [float, str]], help='Distance to new location.')
    _add_flag(flags, 'initial-bearing', help='Angle to new location.')
    _add_flag(flags, 'forward-bearing', help='Angle to new location.')
    _add_flag(flags, '--inverse', action="store_true",
              help='Find new location given a starting position, distance, and angle')
    _add_flag(flags, 'lat', help='Latitude of position to transform into pixel.')
    _add_flag(flags, 'long', help='Longitude of position to transform into pixel.')
    _add_flag(flags, '--lat-ts', metavar='float', help='projection latitude of true scale')
    _add_flag(flags, '--lat-0', metavar='float', help='projection latitude of origin')
    _add_flag(flags, '--long-0', metavar='float', help='projection central meridian')
    _add_flag(flags, 'lat-ts', help='projection latitude of true scale')
    _add_flag(flags, 'lat-0', help='projection latitude of origin')
    _add_flag(flags, 'long-0', help='projection central meridian')
    _add_flag(flags, 'delta-time', help='Amount of time spent getting between the two positions in minutes.')
    _add_flag(flags, '-p', '--print', '--no-save', action='store_true', dest='no_save',
              help='print data to shell without saving')
    _add_flag(flags, '-s', '--save-directory', metavar='path-name',
              help='directory to save to. Defaults to where script was ran')
    _add_flag(flags, '--from-lat-long', metavar='',
              help='Switches to taking latitudes and longitudes as arguments. '
                   'Use the args --from-lat-long -h for more information.')
    _add_flag(flags, '-j', '--j', metavar='int', nargs=1, type=int, help='row to run calculations on')
    _add_flag(flags, '-i', '--i', metavar='int', nargs=1, type=int, help='column to run calculations on')
    _add_flag(flags, '--center',
              narg_types=[[float, float, str], [float, float]],
              help='projection y and x coordinate of the center of area. Default: lat long')
    _add_flag(flags, '--pixel-size',
              narg_types=[[float, float, str], [float, float],
                          [float, str], [float]],
              help='projection size of pixels in the y and x direction. If pixels are '
                   'square, i.e. dy = dx, then only one value needs to be entered')
    _add_flag(flags, '--displacement-data', metavar='filename',
              help='filename or list containing displacements')
    _add_flag(flags, '--units', metavar='str',
              help='units that all provided arguments that take units (except center) should be interpreted as')
    _add_flag(flags, '--upper-left-extent',
              narg_types=[[float, float, str], [float, float]],
              help='projection y and x coordinates of the upper left corner of the upper left pixel')
    _add_flag(flags, '--radius',
              narg_types=[[float], [float, str], [float, float, str],
                          [float, float]],
              help='projection length from the center to the left/rightand top/bottom outer edges')
    _add_flag(flags, '--area-extent',
              narg_types=[[float for i in range(4)] + [str], [float for i in range(4)]],
              help='area extent in projection space: lower_left_y, lower_left_x, upper_right_y, upper_right_x')
    _add_flag(flags, '--shape', nargs=2, type=int, help='number of pixels in the y and x direction')
    _add_flag(flags, '--projection', metavar='str', help='name of projection that the image is in')
    _add_flag(flags, '--earth-ellipsoid', '--earth-spheroid',
              narg_types=[[str], [str, float], [str, float, str], [str, float, str, float],
                          [str, float, str, str, float], [str, float, str, float, str],
                          [str, float, str, str, float, str]],
              help='Ellipsoid of Earth. Coordinate system name or defined '
                   'using a combination of a, b, e, es, f, and rf.')
    _add_flag(flags, '--projection-ellipsoid', '--projection-spheroid',
              narg_types=[[str], [str, float], [str, float, str], [str, float, str, float],
                          [str, float, str, str, float], [str, float, str, float, str],
                          [str, float, str, str, float, str]],
              help='Ellipsoid of projection. Coordinate system name or defined '
                   'using a combination of a, b, e, es, f, and rf.')
    _add_flag(flags, '--precision', default=2, metavar='int',
              help='Number of decimal places to round printed output to, defaults to 2.')
    for flag in flag_names:
        my_parser.add_argument(*flags[flag]['args'], **flags[flag]['kwargs'])
    return my_parser


def _parse_args(flag_names, description):
    """Reads command line arguments and handles logic behind them."""
    parser = _make_parser(flag_names, description)
    commands = {key.replace('-', '_'): val for key, val in vars(parser.parse_args()).items()}
    commands.pop('from_lat_long', None)
    # Logging setup.
    levels = [logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG]
    logging_format = '[%(levelname)s: %(asctime)s : %(name)s] %(message)s'
    logging.basicConfig(level=levels[min(3, commands.pop('verbose'))], format=logging_format,
                        datefmt='%Y-%m-%d %H:%M:%S')
    return commands


def run_script(func, flag_names, output_format, name):
    """Runs python function from wind_functions.py."""
    commands = _parse_args(flag_names, func.__doc__.splitlines()[0])
    precision = commands.pop('precision')
    if name == 'wind_info':
        commands['timestamp'] = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    displacement_data = commands.get('displacement_data')
    if name == 'wind_info_fll':
        commands.pop('no_save', None)
    if displacement_data is None and name in ['velocity', 'vu', 'wind_info', 'area', 'displacements']:
        displacement_data = os.path.join(os.getcwd(), '*.flo')
        commands['displacement_data'] = displacement_data
    if isinstance(displacement_data, str):
        files = glob(displacement_data)
        # If there are files, return after reading. Else let area fall through or error.
        if files:
            for file in files:
                commands['displacement_data'] = os.path.abspath(file)
                output = output_format(func(**commands), precision, **commands)
                if output is not None:
                    print(output)
            return
        # File not found error will be raised from trying to find *.flo. Let area calculate as much as possible.
        elif name != 'area':
            func(**commands)
        commands.pop('displacement_data')
    # Only happens with lat_long, area, position_to_pixel, or if non string is given to displacement-data.
    output = output_format(func(**commands), precision, **commands)
    if output is not None:
        print(output)
