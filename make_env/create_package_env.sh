#!/usr/bin/env bash

pip install .
PARENTDIR="$( cd -P "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
#source activate pywinds
#conda-pack
mkdir pywinds
tar -zxvf $PARENTDIR/pywinds.tar.gz -C $PARENTDIR/pywinds
cp $PARENTDIR/run_scripts/* $PARENTDIR/pywinds/.
tar -czvf $PARENTDIR/new_pywinds.tar.gz pywinds
rm -rf $PARENTDIR/pywinds
