from arg_utils import get_args
from wind_functions import get_area
import sys


def main(argv):
    args = get_args(get_area, argv, 2)
    kwargs = args[1]
    args = args[0]
    area = get_area(*args, **kwargs)
    print(area)
    return area


if __name__ == "__main__":
    main(sys.argv)