from arg_utils import run_script, get_args, print_usage
from wind_functions import velocity, displacements, vu, area, lat_long
import sys


def arg_velocity(argv):
    def output_format(output, kwargs):
        if kwargs.get('save_data') != True:
            return output.tolist()
        return ''

    run_script(velocity, argv, output_format)


def arg_displacements(argv):
    def output_format(output, kwargs):
        if kwargs.get('save_data') != True:
            return output.tolist()
        return ''

    run_script(displacements, argv, output_format)


def arg_vu(argv):
    def output_format(output, kwargs):
        if kwargs.get('save_data') != True:
            return output.tolist()
        return ''

    run_script(vu, argv, output_format)


def arg_area(argv):
    def output_format(output, kwargs):
        if kwargs.get('save_data') != True:
            proj_dict = dict(output.proj_dict)
            if output.height is None or output.width is None:
                shape = None
            else:
                shape = (output.height, output.width)
            return 'projection data: {0}\narea_extent: {1}\nshape: {2}'.format(proj_dict, output.area_extent, shape)
        return ''

    if '--displacement_data' in argv:
        run_script(area, argv, output_format)
    else:
        try:
            args, kwargs = get_args(area, argv)
            output = area(*args, **kwargs)
            print(output_format(output, kwargs))
        except (TypeError, ValueError, FileNotFoundError, RuntimeError) as err:
            print(err)
            print()
            print_usage(area, argv)
            sys.exit(1)


def arg_lat_long(argv):
    def output_format(output, kwargs):
        if kwargs.get('save_data') != True:
            return output.tolist()
        return ''

    if '--displacement_data' in argv:
        run_script(lat_long, argv, output_format)
    else:
        try:
            args, kwargs = get_args(lat_long, argv)
            output = lat_long(*args, **kwargs)
            print(output_format(output, kwargs))
        except (TypeError, ValueError, FileNotFoundError, RuntimeError) as err:
            print(err)
            print()
            print_usage(lat_long, argv)
            sys.exit(1)


def main(argv):
    functions = {'velocity': arg_velocity, 'vu': arg_vu, 'lat_long': arg_lat_long,
                 'displacements': arg_displacements, 'area': arg_area}
    func = argv.pop(1)
    functions[func](argv)



if __name__ == "__main__":
    main(sys.argv)
