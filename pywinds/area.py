#!/usr/bin/env python3
import ntpath
import os
import sys
from pywinds.wind_functions import area
from pywinds.wrapper_utils import area_to_string, run_script


def output_format(output, kwargs):
    if kwargs.get('no_save') is True:
        return area_to_string(output)
    head, tail = ntpath.split(kwargs['displacement_data'])
    extension = tail or ntpath.basename(head)
    save_directory = os.path.join(os.getcwd(), extension + '_output')
    return 'Saving area to:\n{0}\n{1}'.format(os.path.join(save_directory, 'area.txt'),
                                                   os.path.join(save_directory, 'wind_info.hdf5'))


def main(argv):
    run_script(area, argv, output_format, 'area', is_area=True)


if __name__ == "__main__":
    main(sys.argv)
