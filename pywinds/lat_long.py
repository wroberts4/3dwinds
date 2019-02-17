from arg_utils import run_script, get_args, print_usage
from wind_functions import compute_lat_long
import sys


def output_format(output, kwargs):
    if kwargs.get('save_data') != True:
        return output.tolist()
    return ''


def main(argv):
    if '--displacement_data' in argv:
        run_script(compute_lat_long, argv, output_format)
    else:
        try:
            args, kwargs = get_args(compute_lat_long, argv)
            output = compute_lat_long(*args, **kwargs)
            print(output_format(output, kwargs))
        except (TypeError, ValueError, FileNotFoundError, RuntimeError) as err:
            print(err)
            print()
            print_usage(compute_lat_long, argv)
            sys.exit(1)


if __name__ == "__main__":
    main(sys.argv)