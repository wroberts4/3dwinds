Installing pywinds
==================

.. warning::

    Option 1 and option 2 are separate: Updating one will not update the other.

Package Usage Option 1
----------------------

If using pywinds from a tarball, everything should already be setup and ready to go after you untar it
(ie: tar -zxf linux_pywinds.tar.gz). The tarball can be found on 3dwinds.ssec.wisc.edu:/home/wroberts.
New releases of pywinds will be put on 3dwinds.ssec.wisc.edu:/home/wroberts and will need to be
untared to users' directories every time an update is made.

.. note::

    This is different than the git installation. The tarball is not meant to be updated by users. If you
    wish to have pywinds in your virtual environment, install the package into a conda environment (see below).

Package Usage Option 2
----------------------

If installing the package, you will need to use `anaconda for python 3 <https://www.anaconda.com/distribution/>`_.
Source code is available to clone on https://github.com/wroberts4/pywinds. If you are unfamiliar with creating
and managing virtual environments, please see
https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html for more information.
Run these commands again to update your environment every time a change is made to pywinds.


Conda commands to install pywinds::

    $ conda install -c conda-forge python=3.7.3 numpy pyproj xarray pyresample netcdf4
    $ pip install git+https://github.com/wroberts4/pywinds.git

Or use the yaml (only if you have the git repository on your machine)::

    $ git clone https://github.com/wroberts4/pywinds.git
    Cloning into 'pywinds'...
    remote: Enumerating objects: 23, done.
    remote: Counting objects: 100% (23/23), done.
    remote: Compressing objects: 100% (23/23), done.
    remote: Total 10942 (delta 2), reused 6 (delta 0), pack-reused 10919
    Receiving objects: 100% (10942/10942), 720.97 MiB | 22.34 MiB/s, done.
    Resolving deltas: 100% (3242/3242), done.
    $ ls
    pywinds
    $ conda env update -f ./pywinds/build_environment.yml
    $ pip install ./pywinds


Dependencies
------------

pywinds depends on python=3.7.3, pyproj=2.2.1, numpy=1.16.4, xarray=0.12.2, pyresample=1.12.3, and netcdf4=1.5.1.2

If you are making the docs, sphinx=2.1.2 and sphinx-rtd-theme=0.4.3

If you are packing the environment, conda-pack=0.3.1

.. note::

    All versions were used at development time and later or previous versions of each package may work.