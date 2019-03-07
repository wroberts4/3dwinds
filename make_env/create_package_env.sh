#!/usr/bin/env bash

PARENTDIR="$( cd -P "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
. ~/anaconda3/etc/profile.d/conda.sh
conda activate pywinds
pip install $PARENTDIR/../.
rm $PARENTDIR/new_pywinds.tar.gz
conda-pack -o $PARENTDIR/new_pywinds.tar.gz
rm -rf $PARENTDIR/pywinds
mkdir $PARENTDIR/pywinds
mkdir $PARENTDIR/pywinds/env
tar -zxvf $PARENTDIR/new_pywinds.tar.gz -C $PARENTDIR/pywinds/env
sphinx-build ../docs/source $PARENTDIR/pywinds/docs
cp $PARENTDIR/run_scripts/* $PARENTDIR/pywinds/.
cp $PARENTDIR/../setup.py $PARENTDIR/pywinds/.
cp -r $PARENTDIR/../pywinds $PARENTDIR/pywinds/.
tar -czvf $PARENTDIR/new_pywinds.tar.gz pywinds
rm -rf $PARENTDIR/pywinds
