from arg_utils import get_args
from wind_functions import get_displacements
import sys


def main(argv):
    args = get_args(get_displacements, argv, 1)
    kwargs = args[1]
    args = args[0]
    displacements = get_displacements(*args, **kwargs)
    print('displacements (i, j): {0}\nshape: {1}'.format(*displacements))
    return displacements


if __name__ == "__main__":
    main(sys.argv)