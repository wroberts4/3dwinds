#!/usr/bin/env python
import ntpath
import os
import sys
import warnings

import numpy as np

from pywinds.wind_functions import wind_info
from pywinds.wrapper_utils import run_script


def output_format(output, kwargs):
    if kwargs.get('no_save') is True:
        return np.round(output, 2).tolist()
    head, tail = ntpath.split(kwargs['displacement_data'])
    extension = tail or ntpath.basename(head)
    save_directory = os.path.join(os.getcwd(), extension + '_output')
    return 'Data saved to the directory {0}'.format(os.path.join(save_directory))


def main(argv):
    run_script(wind_info, argv, output_format, 'wind_info')


if __name__ == "__main__":
    warnings.filterwarnings("ignore", category=UserWarning, module='pyproj')
    main(sys.argv)
