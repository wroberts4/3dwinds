#!/usr/bin/env bash

PARENTDIR="$( cd -P "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
. ~/anaconda3/etc/profile.d/conda.sh
conda activate pyre
pip install $PARENTDIR/../.
rm $PARENTDIR/new_pywinds.tar.gz
pyinstaller $PARENTDIR/pywinds.spec -y --distpath $PARENTDIR/. --clean
rm -rf $PARENTDIR/build
sphinx-build $PARENTDIR/../docs/source $PARENTDIR/pywinds/docs
cp $PARENTDIR/../setup.py $PARENTDIR/pywinds/.
cp -r $PARENTDIR/../pywinds $PARENTDIR/pywinds/.
tar -czvf $PARENTDIR/new_pywinds.tar.gz pywinds
rm -rf $PARENTDIR/pywinds
