from arg_utils import get_args
from wind_functions import get_displacements
import sys


def main(argv):
    args, kwargs = get_args(get_displacements, argv)
    displacements = get_displacements(*args, **kwargs)
    print('displacements (j, i): {0}\nshape: {1}'.format(*displacements))
    return displacements


if __name__ == "__main__":
    main(sys.argv)