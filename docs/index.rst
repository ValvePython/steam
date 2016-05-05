:tocdepth: 10

.. include:: global.rst

``steam`` module documentation
******************************

|pypi| |license|


A python module for intracting with various parts of Steam_.

Visit the `https://github.com/ValvePython/steam <https://github.com/ValvePython/steam>`_.

.. note::
    Python 3 is currently not supported,
    see `issue#10 <https://github.com/ValvePython/steam/issues/10>`_.

Installing
==========

By default the ``steam`` package doesn't install all dependecies.
Add ``[client]`` extra if you are going to use ``SteamClient``.

Install latest version from PYPI::

    pip install -U steam
    pip install -U steam[client]

Install the current dev version from ``github``::

    pip install git+https://github.com/ValvePython/steam
    pip install git+https://github.com/ValvePython/steam#egg=steam[client]

For extras syntax in ``requirements.txt`` see `pip docs <https://pip.pypa.io/en/stable/reference/pip_install/#requirement-specifiers>`_::

Contents
========

.. toctree::
    :maxdepth: 3

    user_guide

.. toctree::
    :maxdepth: 5

    api/index

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

