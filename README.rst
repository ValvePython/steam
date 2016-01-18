|pypi| |license| |coverage| |scru| |master_build|

Module for interacting with various Steam_ features.

**Documentation**: http://valvepython.github.io/steam/

Installation
------------

Install latest version from PYPI::

    pip install -U steam

Install the current dev version from ``github``::

    pip install git+https://github.com/ValvePython/steam

Testing
-------

To run the test suite with the current ``python``, use::

    make test

To run for specific version, setup a ``virtual environment``::

    virtualenv -p python3 py3
    source py3/bin/active
    make test

To run for ``python 2.7``, ``3.3``, ``3.4`` and ``pypy``, assuming you have them installed::

    tox


.. _Steam: https://store.steampowered.com/

.. |pypi| image:: https://img.shields.io/pypi/v/steam.svg?style=flat&label=latest%20version
    :target: https://pypi.python.org/pypi/steam
    :alt: Latest version released on PyPi

.. |license| image:: https://img.shields.io/pypi/l/steam.svg?style=flat&label=license
    :target: https://pypi.python.org/pypi/steam
    :alt: MIT License

.. |coverage| image:: https://img.shields.io/coveralls/ValvePython/steam/master.svg?style=flat
    :target: https://coveralls.io/r/ValvePython/steam?branch=master
    :alt: Test coverage

.. |scru| image:: https://scrutinizer-ci.com/g/ValvePython/steam/badges/quality-score.png?b=master
    :target: https://scrutinizer-ci.com/g/ValvePython/steam/?branch=master
    :alt: Scrutinizer score

.. |master_build| image:: https://img.shields.io/travis/ValvePython/steam/master.svg?style=flat&label=master
    :target: http://travis-ci.org/ValvePython/steam
    :alt: Build status of master branch
