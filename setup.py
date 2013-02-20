#!/usr/bin/python
from glob import glob
from distutils.core import setup
setup(
   name='screenshot', 
   version='1.0.0', 
   scripts=glob("bin/*"),
)

