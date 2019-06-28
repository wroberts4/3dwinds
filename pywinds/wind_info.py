#!/usr/bin/env python
import ntpath
import os
import logging

import numpy as np

from pywinds.wind_functions import wind_info
from pywinds.wrapper_utils import run_script

logger = logging.getLogger('wind_info.py')


def output_format(output, kwargs):
    if kwargs.get('no_save') is True:
        return np.round(output, 2).tolist()
    head, tail = ntpath.split(kwargs['displacement_data'])
    extension = tail or ntpath.basename(head)
    save_directory = os.path.join(os.getcwd(), extension + '_output')
    logger.info('Data saved to the directory {0}'.format(save_directory))
    return ''


if __name__ == "__main__":
    run_script(wind_info, output_format, 'wind_info')
