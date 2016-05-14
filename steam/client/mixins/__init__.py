"""
All optional features are available as mixins for :class:`steam.client.SteamClient`.
Using this approach the client can remain light yet flexible.
Functionality can be added though inheritance depending on the use case.


Here is quick example of how to use one of the available mixins.

.. code:: python

    from steam import SteamClient
    from stema.client.mixins.friends import Friends


    class MySteamClient(SteamClient, Friends):
        pass

    client = MySteamClient()



Making custom mixing is just as simple.

.. warning::
    Take care not to override existing methods or properties, otherwise bad things will happen

.. note::
    To avoid name collisions of non-public variables and methods, use `Private Variables <https://docs.python.org/2/tutorial/classes.html#private-variables-and-class-local-references>`_

.. code:: python

    class MyMixin(object):
        def __init__(*args, **kwargs):
            super(MyMixin, self).__init__(*args, **kwargs)

            self.my_property = 42

        def my_method(self)
            pass


    class MySteamClient(SteamClient, Friends, MyMixin):
        pass

    client = MySteamClient()

    >>> client.my_property
    42

"""
