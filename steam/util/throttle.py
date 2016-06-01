import sys
import time
import gevent

if sys.version_info >= (3,3):
    _monotonic = time.monotonic
else:
    _monotonic = time.time  # not really monotonic vOv


class ConstantRateLimit(object):
    def __init__(self, times, seconds, exit_wait=False, use_gevent=False):
        """Context manager for enforcing constant rate on code inside the block .

        `rate = seconds / times`

        :param times: times to execute per...
        :type times: :class:`int`
        :param seconds: ...seconds
        :type seconds: :class:`int`
        :param exit_wait: whether to automatically call :meth:`wait` before exiting the block
        :type exit_wait: :class:`bool`
        :param use_gevent: whether to use `gevent.sleep()` instead of `time.sleep()`
        :type use_gevent: :class:`bool`

        Example:

        .. code:: python

            with RateLimiter(1, 5) as r:
                # code taking 1s
                r.wait()  # blocks for 4s
                # code taking 7s
                r.wait()  # doesn't block
                # code taking 1s
                r.wait()  # blocks for 4s
        """
        self.__dict__.update(locals())
        self.rate = float(seconds) / times

    def __enter__(self):
        self._update_ref()
        return self

    def __exit__(self, etype, evalue, traceback):
        if self.exit_wait:
            self.wait()

    def _update_ref(self):
        self._ref = _monotonic() + self.rate

    def wait(self):
        """Blocks until the rate is met"""
        now = _monotonic()
        if now < self._ref:
            delay = max(0, self._ref - now)
            if self.use_gevent:
                gevent.sleep(delay)
            else:
                time.sleep(delay)
        self._update_ref()


