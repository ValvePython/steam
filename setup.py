#!/usr/bin/env python

from setuptools import setup
from codecs import open
from os import path


here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()
with open(path.join(here, 'steam/__init__.py'), encoding='utf-8') as f:
    __version__ = f.readline().split('"')[1]

setup(
    name='steam',
    version=__version__,
    description='Module for interacting with various Steam features',
    long_description=long_description,
    url='https://github.com/ValvePython/steam',
    author="Rossen Georgiev",
    author_email='hello@rgp.io',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Natural Language :: English',
        'Operating System :: OS Independent',
    ],
    keywords='valve steam steamid api webapi',
    packages=['steam'],
    install_requires=[
        'enum34',
        'requests',
        'vdf',
    ],
    zip_safe=True,
)
