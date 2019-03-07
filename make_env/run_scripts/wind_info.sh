#!/usr/bin/env bash

PARENTDIR="$( cd -P "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source $PARENTDIR/env/bin/deactivate
source $PARENTDIR/env/bin/activate
python3 -m pywinds.wind_info "$@"