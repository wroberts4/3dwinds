#!/usr/bin/env bash

set -e
PARENTDIR="$( cd -P "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Remove names that are needed and may have been made in the past.
rm $PARENTDIR/new_pywinds.tar.gz 2> /dev/null ||
rm -r $PARENTDIR/pywinds 2> /dev/null ||

. ~/anaconda3/etc/profile.d/conda.sh
conda env update -n pywinds -f $PARENTDIR/../build_environment.yml
conda activate pywinds
pip install -U --no-deps $PARENTDIR/..
conda clean -afy
conda-pack -o $PARENTDIR/new_pywinds.tar.gz --exclude sphinx
mkdir $PARENTDIR/pywinds
mkdir $PARENTDIR/pywinds/env
tar -xzf $PARENTDIR/new_pywinds.tar.gz -C $PARENTDIR/pywinds/env
mv $PARENTDIR/pywinds/env/bin/*.sh $PARENTDIR/pywinds
mv $PARENTDIR/pywinds/env/bin/*.txt $PARENTDIR/pywinds
rm $PARENTDIR/new_pywinds.tar.gz

find $PARENTDIR/pywinds -follow -type f -name '*.a' -exec rm -f {} \;
find $PARENTDIR/pywinds -follow -type f -name '*.pyc' -exec rm -f {} \;

tar -czf $PARENTDIR/new_pywinds.tar.gz pywinds
rm -r $PARENTDIR/pywinds