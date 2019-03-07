Installing pywinds
==================

pywinds depends on pyproj, numpy, xarray, pyresample, and h5py (and sphinx_rtd_theme for the docs).

Package installation
--------------------

If using pywinds from tarball, everything should already be setup and ready to go after you untar it.

If installing the package, you will need to use anaconda::

    $ conda install -y -c conda-forge pyproj xarray pyresample h5py
    $ conda install -y numpy
    $ pip install .
