from arg_utils import get_args, print_usage
from wind_functions import calculate_velocity
from numpy import ndarray
import sys


def main(argv):
    """Additional command line information

    * You can add units to a specific variable by appending the variable with ":your_unit_here"
      Examples: "--pixel_size 4:km" and "--center 10000,10000:m"
    """
    args, kwargs = get_args(calculate_velocity, argv)
    try:
        velocity = calculate_velocity(*args, **kwargs)
    except (TypeError, ValueError) as err:
        print(err)
        print()
        print_usage(calculate_velocity, argv)
        print(main.__doc__)
        sys.exit(1)
    print(ndarray.tolist(velocity))
    return velocity


if __name__ == "__main__":
    main(sys.argv)
