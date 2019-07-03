#!/usr/bin/env bash

PARENTDIR="$( cd -P "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
. ~/anaconda3/etc/profile.d/conda.sh
conda $PARENTDIR/env/bin/deactivate
conda $PARENTDIR/env/bin/activate
python -W ignore -m pywinds.lat_long "$@"