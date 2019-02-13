from arg_utils import get_args, print_usage
from wind_functions import compute_lat_long
from numpy import ndarray
import sys


def main(argv):
    args, kwargs = get_args(compute_lat_long, argv)
    try:
        lat_long = compute_lat_long(*args, **kwargs)
    except TypeError as err:
        print(err)
        print()
        print_usage(compute_lat_long, argv)
        sys.exit(1)
    print(ndarray.tolist(lat_long))
    return lat_long


if __name__ == "__main__":
    main(sys.argv)