import ast
import numpy as np
import os
import sys
import traceback
from getopt import GetoptError, getopt
from glob import glob
from inspect import getfullargspec
from xarray import DataArray


def area_to_string(area_dict):
    def _round(val, precision):
        if val is None:
            return None
        if np.shape(val) == ():
            return round(val, precision)
        return list(np.round(val, precision).tolist())

    def _param_to_string(param, units, precision):
        param = _round(param, precision)
        return str(param) + ' ' + units if param is not None else None
    precision = 2
    projection = area_dict['projection']
    lat_0 = _param_to_string(area_dict['lat_0'], 'degrees', precision)
    long_0 = _param_to_string(area_dict['long_0'], 'degrees', precision)
    equatorial_radius = _param_to_string(area_dict['equatorial radius'], 'meters', precision)
    eccentricity = _round(area_dict['eccentricity'], 6)
    shape = area_dict['shape']
    area_extent = _param_to_string(area_dict['area_extent'], 'degrees', precision)
    pixel_size = _param_to_string(area_dict['pixel_size'], 'meters', precision)
    center = _param_to_string(area_dict['center'], 'degrees', precision)
    return ('projection: {0}\nlat_0: {1}\nlong_0: {2}\nequatorial radius: {3}\neccentricity: {4}\n'
            'area_extent: {5}\nshape: {6}\npixel_size: {7}\ncenter: {8}').format(projection, lat_0, long_0,
                                                                                 equatorial_radius, eccentricity,
                                                                                 area_extent, shape, pixel_size,
                                                                                 center)


def _arg_to_param(arg):
    """Converts command line arguments (strings) to python data passed to function."""
    units = None
    if len(arg.split(';')) == 2:
        arg, units = arg.split(';')
    try:
        string = ast.literal_eval('%s' % arg)
    except (SyntaxError, ValueError):
        return arg
    if units is not None:
        return DataArray(string, attrs={'units': units})
    return string


def print_usage(func, name):
    """Prints the functions doc_string plus extra command line info."""
    arg_spec = getfullargspec(func)
    num_args = len(arg_spec.args) - len(arg_spec.defaults)
    text_width = 90
    usage_string = 'Usage (' + name + '.sh' + '):'
    length = len(usage_string)
    for arg in ['<' + arg + '>' for arg in getfullargspec(func).args[:num_args]]:
        length = length + len(arg) + 1
        if length > text_width:
            usage_string = usage_string + '\n' + arg
            length = len(arg)
        else:
            usage_string = usage_string + ' ' + arg
    for arg in ['--' + arg + ' <' + arg + '>' for arg in getfullargspec(func).args[num_args:]]:
        length = length + len(arg) + 1
        if length > text_width:
            usage_string = usage_string + '\n' + arg
            length = len(arg)
        else:
            usage_string = usage_string + ' ' + arg
    print(usage_string)
    extra_info = """
    Other usage notes
    -----------------

    * Use the -h or --help flags to print usage"
    """
    print(extra_info)
    print(func.__doc__)


def get_args(func, argv, name):
    """Reads command line arguments and handles logic behind them."""
    if '--help' in argv or '-h' in argv:
        print_usage(func, name)
        sys.exit(0)
    arg_spec = getfullargspec(func)
    num_args = len(arg_spec.args) - len(arg_spec.defaults)
    flags = arg_spec.args[num_args:]
    defaults = dict(zip(arg_spec.args[num_args:], arg_spec.defaults))
    for flag in flags:
        if not isinstance(defaults[flag], bool):
            defaults[flag + '='] = defaults[flag]
            defaults.pop(flag)
    defaults['help'] = ''
    try:
        optlist, args = getopt(argv[1 + num_args:], 'h', defaults.keys())
        if args:
            raise GetoptError('Too many positional arguments provided: {0}'.format(args[0]))
    except GetoptError as err:
        print(err)
        print()
        print_usage(func, name)
        sys.exit(1)
    kwargs = {}
    for arg in optlist:
        if isinstance(defaults.get(arg[0][2:]), bool):
            kwargs[arg[0][2:]] = not defaults[arg[0][2:]]
        else:
            kwargs[arg[0][2:]] = _arg_to_param(arg[1])
    return [_arg_to_param(arg) for arg in argv[1:num_args + 1]], kwargs


def run_script(func, argv, output_format, name, is_area=False, is_lat_long=False):
    """Runs python function from wind_functions.py."""
    args, kwargs = get_args(func, argv, name)
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
    except (TypeError, ValueError, OSError, RuntimeError, IndexError):
        print(traceback.format_exc())
        print()
        print_usage(func, name)
        sys.exit(1)
