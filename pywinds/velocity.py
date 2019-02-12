from arg_utils import get_args
from wind_functions import calculate_velocity
import sys


def main(argv):
    args = get_args(calculate_velocity, argv, 3)
    kwargs = args[1]
    args = args[0]
    velocity = calculate_velocity(*args, **kwargs)
    print('speed:', '[{0} m/sec, {1}°]'.format(*velocity))
    return velocity


if __name__ == "__main__":
    main(sys.argv)
