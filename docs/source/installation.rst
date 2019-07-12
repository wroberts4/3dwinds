Installing pywinds
==================

pywinds depends on python=3.7.3, pyproj=2.2.1, numpy=1.16.4, xarray=0.12.2, pyresample=1.12.3, and netcdf4=1.5.1.2

If you are making the docs, sphinx=2.1.2 and sphinx-rtd-theme=0.4.3

If you are packing the environment, conda-pack=0.3.1

.. note::

    All versions were used at developement time and later or newer versions of each package may work.

Package installation
--------------------

If using pywinds from a tarball, everything should already be setup and ready to go after you untar it
(ie: tar -zxvf linux_pywinds.tar.gz). The tarball can be found on 3dwinds.ssec.wisc.edu:/home/wroberts.

If installing the package, you will need to use `anaconda <https://www.anaconda.com/distribution/>`_.
Source code is available to clone on https://github.com/wroberts4/pywinds.

Conda commands to install pywinds (if you do not have the git repository on your machine)::

    $ conda install -c conda-forge python=3.7.3 numpy pyproj xarray pyresample netcdf4
    $ pip install git+https://github.com/wroberts4/pywinds.git

Or use the yaml (if you have the git repository on your machine)::

    $ ls
    pywinds
    $ conda env update -n pywinds -f pywinds/build_environment.yml
    $ pip install pywinds

