#!/usr/bin/env bash

PARENTDIR="$( cd -P "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
. ~/anaconda3/etc/profile.d/conda.sh
conda activate pywinds
pip install ../.
rm $PARENTDIR/new_pywinds.tar.gz
conda-pack -o $PARENTDIR/new_pywinds.tar.gz --exclude conda-pack --exclude sphinx
rm -rf $PARENTDIR/pywinds
mkdir $PARENTDIR/pywinds
cp $PARENTDIR/run_scripts/* $PARENTDIR/pywinds/.
mkdir $PARENTDIR/pywinds/env
tar -zxvf $PARENTDIR/new_pywinds.tar.gz -C $PARENTDIR/pywinds/env
rm $PARENTDIR/new_pywinds.tar.gz
tar -czvf $PARENTDIR/new_pywinds.tar.gz pywinds
rm -rf $PARENTDIR/pywinds
