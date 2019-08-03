#!/usr/bin/env bash

PARENTDIR="$( cd -P "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source $PARENTDIR/env/bin/activate 2> /dev/null
# https://stackoverflow.com/questions/8063228/how-do-i-check-if-a-variable-exists-in-a-list-in-bash
if [[ $* =~ (^|[[:space:]])"--inverse"($|[[:space:]]) ]]; then
    func=loxodrome_fwd
else
    func=loxodrome_bck
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
    kwargs_names = ['--earth-ellipsoid', '--units']
    if "$func" == "loxodrome_fwd":
        sys.argv.remove('--inverse')
        args_names = ['old-lat', 'old-long', 'distance', 'forward-bearing']
    else:
        args_names = ['old-lat', 'old-long', 'new-lat', 'new-long']
    run_script($func, kwargs_names + args_names, output_format, "$func")
EOF