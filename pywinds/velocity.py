from arg_utils import run_script
from wind_functions import calculate_velocity
import sys


def output_format(output, kwargs):
    if kwargs.get('save_data') != True:
        return output.tolist()
    return ''


def main(argv):
    run_script(calculate_velocity, argv, output_format)


if __name__ == "__main__":
    main(sys.argv)
