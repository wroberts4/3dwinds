#!/usr/bin/env python3
import ntpath
import os
import sys
import numpy as np
from pywinds.wind_functions import lat_long
from pywinds.wrapper_utils import run_script


def output_format(output, kwargs):
    if kwargs.get('no_save') is True:
        return np.round(output, 2).tolist()
    head, tail = ntpath.split(kwargs['displacement_data'])
    extension = tail or ntpath.basename(head)
    save_directory = os.path.join(os.getcwd(), extension + '_output')
    return 'Saving lat_long to:\n{0}\n{1}\n{2}'.format(os.path.join(save_directory, 'old_latitude.txt'),
                                                       os.path.join(save_directory, 'old_longitude.txt'),
                                                       os.path.join(save_directory, 'new_latitude.txt'),
                                                       os.path.join(save_directory, 'new_longitude.txt'),
                                                       os.path.join(save_directory, 'wind_info.hdf5'))


def main(argv):
    run_script(lat_long, argv, output_format, 'lat_long', is_lat_long=True)


if __name__ == "__main__":
    main(sys.argv)
