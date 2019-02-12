from getopt import getopt, GetoptError
from inspect import getfullargspec
from xarray import DataArray
import sys


def _try_num(string):
    if not string:
        return None
    try:
        if float(string) == int(string):
            return int(string)
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


def _print_usage(func, argv, num_args):
    print('Usage (' + argv[0].split('/')[-1].replace('.py', '.sh') + '):',
          *['<' + arg + '>' for arg in getfullargspec(func).args[:num_args]],
          *['--' + arg + ' <' + arg + '>' for arg in getfullargspec(func).args[num_args:]])
    print()
    print(func.__doc__)


# TODO: MAKE TRUE/FALSE ARGS NON-INPUT FLAGS
def get_args(func, argv, num_args):
    try:
        optlist, args = getopt(argv[1 + num_args:], '',
                               [arg + '=' for arg in getfullargspec(func).args[num_args:]] + ['help'])
        if 2 * len(optlist) != len(argv[1:]) - num_args and '--help' not in argv[1:]:
            raise GetoptError('Incorrect number of arguments provided arguments provided')
    except GetoptError as err:
        print(err)
        _print_usage(func, argv, num_args)
        sys.exit(1)
    kwargs = {}
    for duo in optlist:
        if duo[0] == '--help':
            _print_usage(func, argv, num_args)
            sys.exit(0)
        kwargs[duo[0][2:]] = _arg_to_param(duo[1])
    return argv[1:num_args + 1], kwargs
