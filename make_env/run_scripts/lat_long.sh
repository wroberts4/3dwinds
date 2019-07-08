#!/usr/bin/env bash

PARENTDIR="$( cd -P "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source $PARENTDIR/env/bin/activate  2> /dev/null
python -W ignore<<EOF
import numpy as np
import sys

from os.path import abspath
from pywinds.wind_functions import lat_long
from pywinds.wrapper_utils import run_script


def output_format(output, **kwargs):
    return np.round(output, 2).tolist()


if __name__ == "__main__":
    sys.argv = [abspath("$0")] + "$*".split(' ')
    run_script(lat_long, output_format, 'lat_long')
EOF