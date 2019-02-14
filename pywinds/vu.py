from arg_utils import get_args, print_usage
from wind_functions import v_u_component
from numpy import ndarray
import sys


def main(argv):
    """Additional command line information

    * You can add units to a specific variable by appending the variable with ":your_unit_here"
      Examples: "--pixel_size 4:km" and "--center 10000,10000:m"
    """
    args, kwargs = get_args(v_u_component, argv)
    try:
        u_v = v_u_component(*args, **kwargs)
    except TypeError as err:
        print(err)
        print()
        print_usage(v_u_component, argv)
        print(main.__doc__)
        sys.exit(1)
    print(ndarray.tolist(u_v))
    return u_v


if __name__ == "__main__":
    main(sys.argv)