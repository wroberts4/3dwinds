#!/usr/bin/env bash

PARENTDIR="$( cd -P "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source $PARENTDIR/env/bin/activate  2> /dev/null
python -W ignore<<EOF
import sys

from os.path import abspath
from pywinds.wind_functions import area
from pywinds.wrapper_utils import area_to_string, run_script


def output_format(output, precision, **kwargs):
    return area_to_string(output, round_nums=precision)


if __name__ == "__main__":
    sys.argv = [abspath("$0")] + "$*".split(' ')
    kwargs_names = ['--displacement-data', '--projection', '--area-extent', '--shape',
                    '--center', '--pixel-size', '--upper-left-extent', '--radius', '--units', '--projection-ellipsoid']
    args_names = ['lat-ts', 'lat-0', 'long-0']
    run_script(area, kwargs_names + args_names, output_format, 'area')
EOF
