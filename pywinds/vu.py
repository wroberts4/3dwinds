#!/usr/bin/env python
from pywinds.wrapper_utils import run_script
from pywinds.wind_functions import vu
import sys
import numpy as np
import os
import ntpath


def output_format(output, kwargs):
    if kwargs.get('no_save') is True:
        return np.round(output, 2).tolist()
    head, tail = ntpath.split(kwargs['displacement_data'])
    extension = tail or ntpath.basename(head)
    save_directory = os.path.join(os.getcwd(), extension + '_output')
    return 'Saving vu to:\n{0}\n{1}\n{2}'.format(os.path.join(save_directory, 'v.txt'),
                                            os.path.join(save_directory, 'u.txt'),
                                            os.path.join(save_directory, 'wind_info.hdf5'))


def main(argv):
    run_script(vu, argv, output_format, 'vu')


if __name__ == "__main__":
    main(sys.argv)
