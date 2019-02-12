from arg_utils import get_args
from wind_functions import u_v_component
import sys


def main(argv):
    args, kwargs = get_args(u_v_component, argv)
    u_v = u_v_component(*args, **kwargs)
    print('(u, v):', '[{0} m/sec, {1} m/sec]'.format(*u_v))
    return u_v


if __name__ == "__main__":
    main(sys.argv)