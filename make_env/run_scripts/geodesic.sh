#!/usr/bin/env bash

PARENTDIR="$( cd -P "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source $PARENTDIR/env/bin/activate 2> /dev/null
# https://stackoverflow.com/questions/8063228/how-do-i-check-if-a-variable-exists-in-a-list-in-bash
if [[ $* =~ (^|[[:space:]])"--inverse"($|[[:space:]]) ]]; then
    func=geodesic_fwd
else
    func=geodesic_bck
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
    if "$func" == "geodesic_fwd":
        sys.argv.remove('--inverse')
        flag_names = ['old-lat', 'old-long', 'distance', 'initial-bearing', '--earth-ellipsoid', '--units']
    else:
        flag_names = ['old-lat', 'old-long', 'new-lat', 'new-long', '--earth-ellipsoid', '--units']
    run_script($func, flag_names, output_format, "$func")
EOF