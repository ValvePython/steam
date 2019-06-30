#!/usr/bin/env python

from setuptools import setup, find_packages
from codecs import open
from os import path
import sys

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()\
                        .replace('.io/en/latest/', '.io/en/stable/')\
                        .replace('?badge=latest', '?badge=stable')\
                        .replace('projects/steam/badge/?version=latest', 'projects/steam/badge/?version=stable')
with open(path.join(here, 'steam/__init__.py'), encoding='utf-8') as f:
    __version__ = f.readline().split('"')[1]

install_requires = [
    'six>=1.10',
    'pycryptodomex>=3.7.0',
    'requests>=2.9.1,<2.22.0',
    'vdf>=2.0',
    'gevent>=1.2.0',
    'protobuf>=3.0.0',
    'gevent-eventemitter>=2.0',
    'cachetools>=3.0.0',
]

install_extras = {
    'client': [],
}

if sys.version_info < (3, 4):
    install_requires.append('enum34>=1.0.4')

setup(
    name='steam',
    version=__version__,
    description='Module for interacting with various Steam features',
    long_description=long_description,
    url='https://github.com/ValvePython/steam',
    author="Rossen Georgiev",
    author_email='rossen@rgp.io',
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Natural Language :: English',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
    keywords='valve steam steamid api webapi steamcommunity',
    packages=['steam'] + ['steam.'+x for x in find_packages(where='steam')],
    install_requires=install_requires,
    extras_require=install_extras,
    zip_safe=True,
)
