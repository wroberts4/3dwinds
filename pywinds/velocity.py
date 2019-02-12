from arg_utils import get_args
from wind_functions import calculate_velocity
import sys


def main(argv):
    args, kwargs = get_args(calculate_velocity, argv)
    velocity = calculate_velocity(*args, **kwargs)
    print('speed:', '[{0} m/sec, {1}°]'.format(*velocity))
    return velocity


if __name__ == "__main__":
    main(sys.argv)
