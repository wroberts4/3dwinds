#!/bin/bash

# https://stackoverflow.com/questions/9889938/shell-script-current-directory
PARENTDIR="$( cd "$( dirname "$0" )" && pwd )"
python ${PARENTDIR}/wrapper_functions.py velocity $*
