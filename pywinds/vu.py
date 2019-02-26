from wrapper_utils import run_script
from wind_functions import vu
import sys
import numpy as np
import ast


def nparray_to_list(array):
    if len(np.shape(array)) == 1:
        return [num for num in array]
    return [nparray_to_list(new_array) for new_array in array]


def output_format(output, kwargs):
    if kwargs.get('no_save') is True:
        output = nparray_to_list(np.float32(np.round(output, 2)))
        return output
    return ''


def main(argv):
    run_script(vu, argv, output_format, 'vu')


if __name__ == "__main__":
    main(sys.argv)
