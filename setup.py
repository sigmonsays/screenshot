#!/usr/bin/python
from glob import glob
from setuptools import setup, find_packages

install_requires = [
    'boto',
    'pyimgur',
    'pytumblr',
]
setup(
   name='screenshot', 
   version='1.0.0', 
   packages=find_packages('.'),
   install_requires=install_requires,
   zip_safe=False,
   entry_points = {
    'console_scripts': [
        'screenshot = screenshot.cli:main',
    ]
   }

)

