#!/usr/bin/env python

from distutils.core import setup
from glob import glob

setup(name='pywinds',
      version='1.0',
      author='William Roberts',
      author_email='wroberts4@wisc.edu',
      url='https://github.com/wroberts4/pywinds',
      install_requires='sphinx_rtd_theme',
      packages=['pywinds'],
      scripts=glob('make_env/run_scripts/*'))
