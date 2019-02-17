from arg_utils import run_script
from wind_functions import v_u_component
import sys


def output_format(output, kwargs):
    if kwargs.get('save_data') != True:
        return output.tolist()
    return ''


def main(argv):
    run_script(v_u_component, argv, output_format)


if __name__ == "__main__":
    main(sys.argv)