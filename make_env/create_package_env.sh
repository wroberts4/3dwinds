#!/usr/bin/env bash

set -e
PARENTDIR="$( cd -P "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Remove names that are needed and may have been made in the past.
rm $PARENTDIR/pywinds.tar.gz 2> /dev/null ||
rm -r $PARENTDIR/pywinds 2> /dev/null ||

. ~/anaconda3/etc/profile.d/conda.sh
conda env update -n pywinds -f $PARENTDIR/../build_environment.yml
# BUG: conda activate not always found.
conda activate pywinds
pip install -U --no-deps $PARENTDIR/..
conda clean -afy
mkdir $PARENTDIR/pywinds
mkdir $PARENTDIR/pywinds/env
conda-pack --n-threads -1 --compress-level 0 -d $PARENTDIR/pywinds/env --exclude *.a
tar -xzf $PARENTDIR/pywinds.tar.gz -C $PARENTDIR/pywinds/env
mv $PARENTDIR/pywinds/env/bin/*.sh $PARENTDIR/pywinds
mv $PARENTDIR/pywinds/env/bin/*.txt $PARENTDIR/pywinds
rm $PARENTDIR/pywinds.tar.gz

tar -czf $PARENTDIR/pywinds.tar.gz pywinds
rm -r $PARENTDIR/pywinds