from arg_utils import get_args, print_usage
from wind_functions import get_area
import sys


def main(argv):
    args, kwargs = get_args(get_area, argv)
    try:
        area = get_area(*args, **kwargs)
    except TypeError as err:
        print(err)
        print()
        print_usage(get_area, argv)
        sys.exit(1)
    print(area)
    return area


if __name__ == "__main__":
    main(sys.argv)