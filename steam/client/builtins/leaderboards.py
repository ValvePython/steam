"""
Reading the leaderboards with :class:`SteamLeaderboard` is as easy as iterating over a list.
"""
import logging
from steam.core.msg import MsgProto
from steam.enums import EResult, ELeaderboardDataRequest, ELeaderboardSortMethod, ELeaderboardDisplayType
from steam.enums.emsg import EMsg
from steam.utils import _range, chunks
from steam.utils.throttle import ConstantRateLimit


class Leaderboards(object):
    def __init__(self, *args, **kwargs):
        super(Leaderboards, self).__init__(*args, **kwargs)

    def get_leaderboard(self, app_id, name):
        """.. versionadded:: 0.8.2

        Find a leaderboard

        :param app_id: application id
        :type app_id: :class:`int`
        :param name: leaderboard name
        :type name: :class:`str`
        :return: leaderboard instance
        :rtype: :class:`SteamLeaderboard`
        :raises: :class:`LookupError` on message timeout or error
        """
        message = MsgProto(EMsg.ClientLBSFindOrCreateLB)
        message.header.routing_appid = app_id
        message.body.app_id = app_id
        message.body.leaderboard_name = name
        message.body.create_if_not_found = False

        resp = self.send_job_and_wait(message, timeout=15)

        if not resp:
            raise LookupError("Didn't receive response within 15seconds :(")
        if resp.eresult != EResult.OK:
            raise LookupError(EResult(resp.eresult))

        return SteamLeaderboard(self, app_id, name, resp)


class SteamLeaderboard(object):
    """.. versionadded:: 0.8.2

    Steam leaderboard object.
    Generated via :meth:`Leaderboards.get_leaderboard()`
    Works more or less like a :class:`list` to access entries.

    .. note::
        Each slice will produce a message to steam.
        Steam and protobufs might not like large slices.
        Avoid accessing individual entries by index and instead use iteration or well sized slices.

    Example usage:

    .. code:: python

        lb = client.get_leaderboard(...)

        for entry in lb[:100]:  # top 100
            print entry
    """
    ELeaderboardDataRequest = ELeaderboardDataRequest
    ELeaderboardSortMethod = ELeaderboardSortMethod
    ELeaderboardDisplayType = ELeaderboardDisplayType

    app_id = 0
    name = ''  #: leaderboard name
    id = 0 #: leaderboard id
    entry_count = 0
    sort_method = ELeaderboardSortMethod.NONE      #: :class:`steam.enums.common.ELeaderboardSortMethod`
    display_type = ELeaderboardDisplayType.NONE    #: :class:`steam.enums.common.ELeaderboardDisplayType`
    data_request = ELeaderboardDataRequest.Global  #: :class:`steam.enums.common.ELeaderboardDataRequest`

    def __init__(self, steam, app_id, name, data=None):
        self._steam = steam
        self.app_id = app_id

        if data is not None:
            for field in data.DESCRIPTOR.fields:
                if field.name.startswith('leaderboard_'):
                    self.__dict__[field.name.replace('leaderboard_', '')] = getattr(data, field.name)

        self.sort_method = ELeaderboardSortMethod(self.sort_method)
        self.display_type = ELeaderboardDisplayType(self.display_type)

    def __repr__(self):
        return "<%s(%d, %s, %d, %s, %s)>" % (
            self.__class__.__name__,
            self.app_id,
            repr(self.name),
            len(self),
            self.sort_method,
            self.display_type,
            )

    def __len__(self):
        return self.entry_count

    def get_entries(self, start=0, end=0, data_request=None, steam_ids=None):
        """Get leaderboard entries.

        :param start: start entry, not index (e.g. rank 1 is ``start=1``)
        :type start: :class:`int`
        :param end: end entry, not index (e.g. only one entry then ``start=1,end=1``)
        :type end: :class:`int`
        :param data_request: data being requested
        :type data_request: :class:`steam.enums.common.ELeaderboardDataRequest`
        :param steam_ids: list of steam ids when using :attr:`.ELeaderboardDataRequest.Users`
        :type steamids: :class:`list`
        :return: a list of entries, see ``CMsgClientLBSGetLBEntriesResponse``
        :rtype: :class:`list`
        :raises: :class:`LookupError` on message timeout or error
        """
        message = MsgProto(EMsg.ClientLBSGetLBEntries)
        message.body.app_id = self.app_id
        message.body.leaderboard_id = self.id
        message.body.range_start = start
        message.body.range_end = end
        message.body.leaderboard_data_request = self.data_request if data_request is None else data_request

        if steam_ids:
            message.body.steamids.extend(steam_ids)

        resp = self._steam.send_job_and_wait(message, timeout=15)

        if not resp:
            raise LookupError("Didn't receive response within 15seconds :(")
        if resp.eresult != EResult.OK:
            raise LookupError(EResult(resp.eresult))

        if resp.HasField('leaderboard_entry_count'):
            self.entry_count = resp.leaderboard_entry_count

        return resp.entries

    def __getitem__(self, x):
        if isinstance(x, slice):
            stop_max = len(self)
            start = 0 if x.start is None else x.start if x.start >= 0 else max(0, x.start + stop_max)
            stop = stop_max if x.stop is None else x.stop if x.stop >= 0 else max(0, x.stop + stop_max)
            step = x.step or 1
            if step < 0:
                start, stop = stop, start
            step = abs(step)

            if start >= stop: return []
        else:
            if x < 0: x += self.entry_count
            start, stop, step = x, x + 1, 1

            if x < 0 or x >= self.entry_count:
                raise IndexError('list index out of range')

        entries = self.get_entries(start+1, stop)

        if isinstance(x, slice):
            return [entries[i] for i in _range(0, len(entries), step)]
        else:
            return entries[0]

    def get_iter(self, times, seconds, chunk_size=2000):
        """Make a iterator over the entries

        See :class:`steam.util.throttle.ConstantRateLimit` for ``times`` and ``seconds`` parameters.

        :param chunk_size: number of entries per request
        :type chunk_size: :class:`int`
        :returns: generator object
        :rtype: :class:`generator`

        The iterator essentially buffers ``chuck_size`` number of entries, and ensures
        we are not sending messages too fast.
        For example, the ``__iter__`` method on this class uses ``get_iter(1, 1, 2000)``
        """
        def entry_generator():
            with ConstantRateLimit(times, seconds, sleep_func=self._steam.sleep) as r:
                for entries in chunks(self, chunk_size):
                    if not entries:
                        return
                    for entry in entries:
                        yield entry
                    r.wait()
        return entry_generator()

    def __iter__(self):
        return self.get_iter(1, 1, 2000)
