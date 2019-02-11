from pywinds.arg_utils import get_kwargs
from pywinds.wind_functions import calculate_velocity
import sys


def main(argv):
    velocity = calculate_velocity(argv[1], argv[2], argv[3], **get_kwargs(calculate_velocity, argv, 3))
    print('speed:', '{0} m/sec, {1}°'.format(*velocity))
    return velocity


if __name__ == "__main__":
    main(sys.argv)
