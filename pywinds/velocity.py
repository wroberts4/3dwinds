from wrapper_utils import run_script
from wind_functions import velocity
import sys
import numpy as np


def output_format(output, kwargs):
    if kwargs.get('no_save') is True:
        return np.round(output, 2).tolist()
    return ''


def main(argv):
    run_script(velocity, argv, output_format, 'velocity')


if __name__ == "__main__":
    main(sys.argv)
