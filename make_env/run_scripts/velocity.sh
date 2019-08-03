#!/usr/bin/env bash

PARENTDIR="$( cd -P "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source $PARENTDIR/env/bin/activate  2> /dev/null
# https://stackoverflow.com/questions/8063228/how-do-i-check-if-a-variable-exists-in-a-list-in-bash
if [[ $* =~ (^|[[:space:]])"--from-lat-long"($|[[:space:]]) ]]; then
    func=velocity_fll
else
    func=velocity
fi
python -W ignore<<EOF
import numpy as np
import sys

from os.path import abspath
from pywinds.wind_functions import $func
from pywinds.wrapper_utils import run_script


def output_format(output, precision, **kwargs):
    return np.round(output, precision).tolist()


if __name__ == "__main__":
    sys.argv = [abspath("$0")] + "$*".split(' ')
    if "$func" == "velocity_fll":
        sys.argv.remove('--from-lat-long')
        kwargs_names = ['--earth-ellipsoid']
        args_names = ['delta-time', 'old-lat', 'old-long', 'new-lat', 'new-long']
    else:
        kwargs_names = ['--pixel-size', '--displacement-data', '--projection', '-j', '-i', '--area-extent', '--shape',
                        '--center', '--upper-left-extent', '--radius', '--units', '--projection-ellipsoid',
                        '--earth-ellipsoid', '--from-lat-long']
        args_names = ['lat-ts', 'lat-0', 'long-0', 'delta-time']
    run_script($func, kwargs_names + args_names, output_format, "$func")
EOF