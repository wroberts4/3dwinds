Installing pywinds
==================

pywinds depends on pyproj, numpy, xarray, pyresample, and netcdf4 (and sphinx_rtd_theme for the docs).

Package installation
--------------------

If using pywinds from a tarball, everything should already be setup and ready to go after you untar it
(ie: tar -zxvf linux_pywinds.tar.gz). The tarball can be found on 3dwinds.ssec.wisc.edu:/home/wroberts.

If installing the package, you will need to use `anaconda <https://www.anaconda.com/distribution/>`_.
Source code is available to clone on https://github.com/wroberts4/pywinds.

Conda commands to install pywinds::

    $ conda install -y python numpy
    $ conda install -y -c conda-forge pyproj xarray pyresample netcdf4
    $ pwd
    /Desktop/pywinds
    $ pip install .

