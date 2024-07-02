# -*- coding: utf-8 -*-
"""
Created on Mon May 17 17:22:46 2021

@author: Federico Calesella
         Psychiatry and Clinical Psychobiology Unit, Division of Neuroscience, 
         IRCCS San Raffaele Scientific Institute, Milan, Italy
"""
from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()
    
setup(name='neurohab',
version='0.0.2',
description='Voxelwise brain habituation',
long_description=readme(),
long_description_content_type='text/markdown',
url='https://github.com/fcalesella/neurohab',
author='Federico Calesella',
author_email='f.calesella@gmail.com',
license='GNU General Public License v3.0',
packages=['neurohab'],
install_requires=['numpy', 'nibabel', 'scipy'])