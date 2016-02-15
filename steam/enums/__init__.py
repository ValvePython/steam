"""This module contains various value enumerations.

They are all based on :py:class:`IntEnum`, which gives them :py:class:`int` properties.
They can be compared to :py:class:`int` and used in places there :py:class:`int` is required.
Like for example, protobuf message.
They also provide a easy way to resolve a name or value for a specific enum.

.. code:: python

    >>> EResult.OK
    <EResult.OK: 1>
    >>> EResult(1)
    <EResult.OK: 1>
    >>> EResult['OK']
    <EResult.OK: 1>
    >>> EResult.OK == 1
    True

.. note::
    all enums from :py:mod:`steam.enum.common` can be imported directly from :py:mod:`steam.enum`
"""

from steam.enums.common import *
