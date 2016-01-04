from collections import defaultdict
import gevent
from gevent.event import AsyncResult


class EventEmitter(object):
    """
    Implements event emitter using gevent library
    """

    def emit(self, event, *args):
        """
        Emit event with some arguments
        """

        if not hasattr(self, '_event_callbacks'):
            return

        gevent.idle()

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
        Removes a callback for the specified event
        """

        if not hasattr(self, '_event_callbacks'):
            return

        self._event_callbacks[event].pop(callback, None)

    def wait_event(self, event, timeout=None):
        """
        Blocks until an event and returns the results
        """
        result = AsyncResult()
        self.on(event, result)
        return result.get(True, timeout)

    def on(self, event, callback=None):
        """
        Registers a callback for the specified event

        Can be as function decorator if only event is specified.
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
