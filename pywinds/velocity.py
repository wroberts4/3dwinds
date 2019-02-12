from arg_utils import get_args, print_usage
from wind_functions import calculate_velocity
import sys


def main(argv):
    args, kwargs = get_args(calculate_velocity, argv)
    try:
        velocity = calculate_velocity(*args, **kwargs)
    except TypeError as err:
        print(err)
        print()
        print_usage(calculate_velocity, argv)
        sys.exit(1)
    print('speed:', '[{0} m/sec, {1}°]'.format(*velocity))
    return velocity


if __name__ == "__main__":
    main(sys.argv)
