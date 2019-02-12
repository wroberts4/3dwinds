from getopt import getopt, GetoptError
from inspect import getfullargspec
from xarray import DataArray
import sys


def _try_num(string):
    if not string or string.lower() == 'none':
        return None
    try:
        if float(string) == int(string):
            return int(string)
    except ValueError:
        pass
    try:
        return float(string)
    except ValueError:
        return string


def _try_list(string):
    try:
        string = string.replace('(', '').replace(')', '').replace('[', '').replace(']', '')
        if len(string.split(',')) != 1:
            return [_try_num(num) for num in string.split(',')]
    except AttributeError:
        pass
    return string


def _arg_to_param(arg):
    units = None
    if len(arg.split(':')) == 2:
        arg, units = arg.split(':')
    string = _try_num(arg)
    if isinstance(string, (float, int)):
        if units is not None:
            return DataArray(string, attrs={'units': units})
        return string
    string = _try_list(string)
    if units is not None:
        return DataArray(string, attrs={'units': units})
    return string


def print_usage(func, argv):
    arg_spec = getfullargspec(func)
    num_args = len(arg_spec.args) - len(arg_spec.defaults)
    print('Usage (' + argv[0].split('/')[-1].replace('.py', '.sh') + '):',
          *['<' + arg + '>' for arg in getfullargspec(func).args[:num_args]],
          *['--' + arg + ' <' + arg + '>' for arg in getfullargspec(func).args[num_args:]])
    print()
    print(func.__doc__)


def get_args(func, argv):
    arg_spec = getfullargspec(func)
    num_args = len(arg_spec.args) - len(arg_spec.defaults)
    flags = arg_spec.args[num_args:]
    defaults = dict(zip(arg_spec.args[num_args:], arg_spec.defaults))
    try:
        for flag in flags:
            if not isinstance(defaults[flag], bool):
                defaults[flag + '='] = defaults[flag]
                defaults.pop(flag)
        defaults['help'] = ''
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
