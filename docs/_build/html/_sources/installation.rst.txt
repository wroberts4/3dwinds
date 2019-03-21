Installing pywinds
==================

pywinds depends on python=3.7.1, pyproj=2.1.1, numpy=1.16.1, xarray=0.12.0, pyresample=1.11.0, and netcdf4=1.4.3.2

If you are making the docs, sphinx=1.8.5 and sphinx-rtd-theme=0.4.3

If you are packing the environment, conda-pack=0.3.1

.. note::

    All versions were used at developement time and later or newer versions of each package may work.

Package installation
--------------------

If using pywinds from a tarball, everything should already be setup and ready to go after you untar it
(ie: tar -zxvf linux_pywinds.tar.gz). The tarball can be found on 3dwinds.ssec.wisc.edu:/home/wroberts.

If installing the package, you will need to use `anaconda <https://www.anaconda.com/distribution/>`_.
Source code is available to clone on https://github.com/wroberts4/pywinds.

Conda commands to install pywinds::

    $ conda install -y -c conda-forge python=3.7.2 numpy=1.16.1 pyproj=2.1.1
      xarray=0.12.0 pyresample=1.11.0 netcdf4=1.4.3.2
    $ pip install git+https://github.com/wroberts4/pywinds.git

