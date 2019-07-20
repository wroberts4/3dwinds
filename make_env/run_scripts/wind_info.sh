#!/usr/bin/env bash

PARENTDIR="$( cd -P "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source $PARENTDIR/env/bin/activate  2> /dev/null
python -W ignore<<EOF
import logging
import ntpath
import os
import sys

import numpy as np

from pywinds.wind_functions import wind_info
from pywinds.wrapper_utils import run_script

logger = logging.getLogger('wind_info.sh')


def output_format(output, precision, **kwargs):
    if kwargs.get('no_save') is True:
        return np.round(output, precision).tolist()
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
    sys.argv = [os.path.abspath("$0")] + "$*".split(' ')
    run_script(wind_info, output_format, 'wind_info')
EOF