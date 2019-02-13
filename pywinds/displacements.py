from arg_utils import get_args, print_usage
from wind_functions import get_displacements
from numpy import ndarray
import sys


def main(argv):
    args, kwargs = get_args(get_displacements, argv)
    try:
        displacements = get_displacements(*args, **kwargs)
    except TypeError as err:
        print(err)
        print()
        print_usage(get_displacements, argv)
        sys.exit(1)
    print(ndarray.tolist(*displacements))
    return displacements


if __name__ == "__main__":
    main(sys.argv)