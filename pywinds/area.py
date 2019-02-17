from arg_utils import run_script, get_args, print_usage
from wind_functions import get_area
import sys


def output_format(output, kwargs):
    if kwargs.get('save_data') != True:
        proj_dict = dict(output.proj_dict)
        if output.height is None or output.width is None:
            shape = None
        else:
            shape = (output.height, output.width)
        return 'projection data: {0}\narea_extent: {1}\nshape: {2}'.format(proj_dict, output.area_extent, shape)
    return ''


def main(argv):
    if '--displacement_data' in argv:
        run_script(get_area, argv, output_format)
    else:
        try:
            args, kwargs = get_args(get_area, argv)
            output = get_area(*args, **kwargs)
            print(output_format(output, kwargs))
        except (TypeError, ValueError, FileNotFoundError, RuntimeError) as err:
            print(err)
            print()
            print_usage(get_area, argv)
            sys.exit(1)


if __name__ == "__main__":
    main(sys.argv)