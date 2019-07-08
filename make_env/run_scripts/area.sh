#!/usr/bin/env bash

PARENTDIR="$( cd -P "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source $PARENTDIR/env/bin/activate  2> /dev/null
python -W ignore<<EOF
import sys

from os.path import abspath
from pywinds.wind_functions import area
from pywinds.wrapper_utils import area_to_string, run_script


def output_format(output, **kwargs):
    return area_to_string(output, round_nums=2)


if __name__ == "__main__":
    sys.argv = [abspath("$0")] + "$*".split(' ')
    run_script(area, output_format, 'area')
EOF
