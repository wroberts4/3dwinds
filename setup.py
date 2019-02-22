#!/usr/bin/env python

from distutils.core import setup

setup(name='pywinds',
      version='1.0',
      author='William Roberts',
      author_email='wroberts4@wisc.edu',
      long_description=open('README.txt').read(),
      packages=['numpy', 'pyproj', 'pyresample'])
