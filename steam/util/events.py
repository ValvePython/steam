from collections import defaultdict
import gevent
from gevent.event import AsyncResult


class EventEmitter(object):
    """
    Implements event emitter using ``gevent`` module.
    Other modules can inherit from this object.

    .. code:: python

        class SomeClass(EventEmitter):
            pass

    """

    def emit(self, event, *args):
        """
        Emit event with some arguments

        :type event: any
        :param args: any or no arguments
        """

        gevent.idle()

        if hasattr(self, '_event_callbacks'):
            for callback in list(self._event_callbacks[event]):
                if isinstance(callback, AsyncResult):
                    self.remove_listener(event, callback)

                    result = args
                    if len(args) == 1:
                        result = args[0]

                    callback.set(result)
                else:
                    gevent.spawn(callback, *args)

                gevent.idle()

        # every event is also emitted as None
        if event is not None:
            self.emit(None, event, *args)

    def remove_listener(self, event, callback):
        """
        Removes callback for the specified event

        :param event: event identifier
        :param callback: callback reference
        :type callback: function, method or :py:class:`gevent.event.AsyncResult`
        """

        if not hasattr(self, '_event_callbacks'):
            return

        self._event_callbacks[event].pop(callback, None)

    def wait_event(self, event, timeout=None):
        """
        Blocks until an event and returns the results

        :param event: event identifier
        :param timeout: seconds to wait before raising an exception
        :type timeout: int
        :return: returns event arguments, if any. If there are many, returns tuple.
        :rtype: None, any, or tuple
        :raises: gevent.Timeout
        """
        result = AsyncResult()
        self.on(event, result)
        return result.get(True, timeout)

    def on(self, event, callback=None):
        """
        Registers a callback for the specified event

        :param event: event name
        :param callback: callback function

        Can be as function decorator if only event is specified.

        .. code:: python

            @instaceOfSomeClass.on("some event")
            def handle_event():
                pass

            instaceOfSomeClass.on("some event", handle_event)

        To listen for any event, use :py:class:`None` as event identifier.
        """

        if not hasattr(self, '_event_callbacks'):
            self._event_callbacks = defaultdict(dict)

        # when used function
        if callback:
            self._event_callbacks[event][callback] = None
            return

        # as decorator
        def wrapper(callback):
            self._event_callbacks[event][callback] = None
            return callback
        return wrapper
