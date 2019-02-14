from getopt import getopt, GetoptError
from inspect import getfullargspec
from xarray import DataArray
import sys
import ast


def _arg_to_param(arg):
    units = None
    if len(arg.split(':')) == 2:
        arg, units = arg.split(':')
    try:
        string = ast.literal_eval('%s' % arg)
    except (SyntaxError, ValueError):
        return arg
    if units is not None:
        return DataArray(string, attrs={'units': units})
    return string


def print_usage(func, argv):
    """
    Other command line notes
    ------------------------

    * You can add units to a specific variable by appending the variable with ":your_unit_here"
      Examples: "--pixel_size 4:km" and "--center [10000,10000]:m"
    """
    arg_spec = getfullargspec(func)
    num_args = len(arg_spec.args) - len(arg_spec.defaults)
    print('Usage (' + argv[0].split('/')[-1].replace('.py', '.sh') + '):',
          *['<' + arg + '>' for arg in getfullargspec(func).args[:num_args]],
          *['--' + arg + ' <' + arg + '>' for arg in getfullargspec(func).args[num_args:]])
    print(print_usage.__doc__)
    print(func.__doc__)


def get_args(func, argv):
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
        print_usage(func, argv)
        sys.exit(1)
    kwargs = {}
    for arg in optlist:
        if arg[0] == '--help' or arg[0] == '-h':
            print_usage(func, argv)
            sys.exit(0)
        elif isinstance(defaults.get(arg[0][2:]), bool):
            kwargs[arg[0][2:]] = not defaults[arg[0][2:]]
        else:
            kwargs[arg[0][2:]] = _arg_to_param(arg[1])
    return [_arg_to_param(arg) for arg in argv[1:num_args + 1]], kwargs
