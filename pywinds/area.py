from arg_utils import get_args
from wind_functions import get_area
import sys


def main(argv):
    args, kwargs = get_args(get_area, argv)
    area = get_area(*args, **kwargs)
    print(area)
    return area


if __name__ == "__main__":
    main(sys.argv)