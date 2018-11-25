Installation Details
====================

Linux
-----

Steps assume that ``python`` and ``pip`` are already installed.

1. Install dependencies (see sections below)
2. Run ``pip install steam``

.. note::
    Consider using `virtualenv <https://virtualenv.pypa.io>`_
    in order to keep you system packages untouched.


Windows
-------

Cygwin
^^^^^^

1. Download cygwin installer from https://cygwin.com/install.html

2. During the setup select these additional packages
    - ``python3``
    - ``python3-setuptools``

4. Install pip
    - Open cygwin terminal
    - Run ``easy_install-3.4 pip``

3. Run ``pip install steam``

.. note::
    Consider using `virtualenv <https://virtualenv.pypa.io>`_
    in order to keep you system packages untouched.

.. note::
    Installation may take a while as a number of dependecies will be compiled


Native Python
^^^^^^^^^^^^^

1. Download & install python 3.5 from https://www.python.org/downloads/windows/

.. note::
    Installing for all users will require administrator rights

2. Then from ``cmd`` run ``pip install steam``

