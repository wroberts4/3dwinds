#!/usr/bin/env bash

PARENTDIR="$( cd -P "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
. ~/Anaconda3/etc/profile.d/conda.sh
conda activate pywinds
pip install $PARENTDIR/../.
rm new_pywinds.tar.gz
conda-pack -o new_pywinds.tar.gz
mkdir pywinds
tar -zxvf $PARENTDIR/new_pywinds.tar.gz -C $PARENTDIR/pywinds
cp $PARENTDIR/run_scripts/* $PARENTDIR/pywinds/.
tar -czvf $PARENTDIR/new_pywinds.tar.gz pywinds
#rm -rf $PARENTDIR/pywinds
