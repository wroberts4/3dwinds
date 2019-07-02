#!/usr/bin/env python
import ntpath
import os
import logging

import numpy as np

from pywinds.wind_functions import wind_info
from pywinds.wrapper_utils import run_script

logger = logging.getLogger('wind_info.py')


def output_format(output, **kwargs):
    if kwargs.get('no_save') is True:
        return np.round(output, 2).tolist()
    displacement_filename = kwargs.get('displacement_data')
    if isinstance(displacement_filename, str):
        if not os.path.isfile(displacement_filename):
            return
        head, tail = ntpath.split(displacement_filename)
        extension = tail or ntpath.basename(head)
    else:
        extension = 'list'
    if isinstance(kwargs.get('save_directory'), str):
        save_directory = os.path.join(os.path.abspath(kwargs['save_directory']),
                                      extension + '_output_' + kwargs['timestamp'])
    else:
        save_directory = os.path.join(os.getcwd(), extension + '_output_' + kwargs['timestamp'])
    logger.info('Data saved to the directory {0}'.format(save_directory))


if __name__ == "__main__":
    run_script(wind_info, output_format, 'wind_info')
