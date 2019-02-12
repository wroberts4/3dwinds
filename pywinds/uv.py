from arg_utils import get_args, print_usage
from wind_functions import u_v_component
import sys


def main(argv):
    args, kwargs = get_args(u_v_component, argv)
    try:
        u_v = u_v_component(*args, **kwargs)
    except TypeError as err:
        print(err)
        print()
        print_usage(u_v_component, argv)
        sys.exit(1)
    print('(u, v):', '[{0} m/sec, {1} m/sec]'.format(*u_v))
    return u_v


if __name__ == "__main__":
    main(sys.argv)