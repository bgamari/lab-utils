#!/usr/bin/env python

from distutils.core import setup

setup(name='rtb-utils',
      version='1.0',
      description='Utilities for interfacing with the Rohde & Schwartz RTB[24]000 series of oscilloscopes',
      author='Ben Gamari',
      author_email='ben@smart-cactus.org',
      py_modules=['rtb', 'spectrum', 'rtb_util'],
      entry_points={
          'console_scripts': [
              'rtb-spectrum=spectrum:main',
              'rtb-util=rtb_util:main'
          ]
      }
     )
