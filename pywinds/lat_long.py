from arg_utils import get_args
from wind_functions import compute_lat_long
import sys


def main(argv):
    args, kwargs = get_args(compute_lat_long, argv)
    lat_long = compute_lat_long(*args, **kwargs)
    print('(latitude, longitude):', '[{0}°, {1}°]'.format(*lat_long))
    return lat_long


if __name__ == "__main__":
    main(sys.argv)