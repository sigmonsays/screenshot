#!/usr/bin/python
from glob import glob
from setuptools import setup, find_packages

install_requires = [
    'boto',
]
setup(
   name='screenshot', 
   version='1.0.0', 
   scripts=glob("bin/*"),
   packages=find_packages('.'),
   install_requires=install_requires,
)

