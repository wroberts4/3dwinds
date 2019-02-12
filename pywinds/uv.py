from arg_utils import get_args
from wind_functions import u_v_component
import sys


def main(argv):
    args = get_args(u_v_component, argv, 3)
    kwargs = args[1]
    args = args[0]
    u_v = u_v_component(*args, **kwargs)
    print('(u, v):', '[{0} m/sec, {1} m/sec]'.format(*u_v))
    return u_v


if __name__ == "__main__":
    main(sys.argv)