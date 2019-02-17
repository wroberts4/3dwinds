from arg_utils import run_script
from wind_functions import get_displacements_and_area
import sys


def output_format(output, kwargs):
    if kwargs.get('save_data') != True:
        return output[0].tolist()
    return ''


def main(argv):
    run_script(get_displacements_and_area, argv, output_format)


if __name__ == "__main__":
    main(sys.argv)
