#!/usr/bin/env bash

PARENTDIR="$( cd -P "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source $PARENTDIR/env/bin/activate  2> /dev/null
python -W ignore -m pywinds.lat_long "$@"