"""
Various features that don't have a category
"""
import logging
from eventemitter import EventEmitter
from steam.core.msg import MsgProto, get_um
from steam.enums import EResult, ELeaderboardDataRequest, ELeaderboardSortMethod, ELeaderboardDisplayType
from steam.enums.emsg import EMsg
from steam.util import WeakRefKeyDict, _range, chunks
from steam.util.throttle import ConstantRateLimit


class Misc(object):
    def __init__(self, *args, **kwargs):
        super(Misc, self).__init__(*args, **kwargs)

        name = "%s.unified_messages" % self.__class__.__name__
        self.unified_messages = SteamUnifiedMessages(self, name)  #: instance of :class:`SteamUnifiedMessages`

    def games_played(self, app_ids):
        """
        Set the application being played by the user

        :param app_ids: a list of application ids
        :type app_ids: :class:`list`
        """
        if not isinstance(app_ids, list):
            raise ValueError("Expected app_ids to be of type list")

        app_ids = map(int, app_ids)

        message = MsgProto(EMsg.ClientGamesPlayed)
        GamePlayed = message.body.GamePlayed

        message.body.games_played.extend(map(lambda x: GamePlayed(game_id=x), app_ids))

        self.send(message)

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

class SteamUnifiedMessages(EventEmitter):
    """Simple API for send/recv of unified messages

    Incoming messages are emitted as events once with their ``jobid``
    and once with their method name (e.g. ``Player.GetGameBadgeLevels#1``)

    Example code:

    .. code:: python

        response = client.unified_messages.send_and_wait('Player.GetGameBadgeLevels#1', {
            'property': 1,
            'something': 'value',
            })

        # or alternatively

        jobid = client.unified_message.send('Player.GetGameBadgeLevels#1', {'something': 1})
        response, = client.unified_message.wait_event(jobid)

        # or

        message = client.unified_message.get('Player.GetGameBadgeLevels#1')
        message.something = 1
        response = client.unified_message.send_and_wait(message)
    """
    def __init__(self, steam, logger_name=None):
        self._LOG = logging.getLogger(logger_name if logger_name else self.__class__.__name__)
        self._steam = steam
        self._data = WeakRefKeyDict()

        steam.on(EMsg.ServiceMethod, self._handle_service_method)
        steam.on(EMsg.ClientServiceMethodResponse, self._handle_client_service_method)

    def emit(self, event, *args):
        if event is not None:
            self._LOG.debug("Emit event: %s" % repr(event))
        EventEmitter.emit(self, event, *args)

    def _handle_service_method(self, message):
        self.emit(message.header.target_job_name, message.body)

    def _handle_client_service_method(self, message):
        method_name = message.body.method_name
        proto = get_um(method_name, response=True)

        if proto is None:
            self._LOG("Unable to find proto for %s" % repr(method_name))
            return

        resp = proto()
        resp.ParseFromString(message.body.serialized_method_response)

        self.emit(method_name, resp)

        jobid = message.header.jobid_target
        if jobid not in (-1, 18446744073709551615):
            self.emit("job_%d" % jobid, resp)

    def get(self, method_name):
        """Get request proto instance for given methed name

        :param method_name: name for the method (e.g. ``Player.GetGameBadgeLevels#1``)
        :type method_name: :class:`str`
        :return: proto message instance, or :class:`None` if not found
        """
        proto = get_um(method_name)
        if proto is None:
            return None
        message = proto()
        self._data[message] = method_name
        return message

    def send(self, message, params=None):
        """Send service method request

        :param message:
            proto message instance (use :meth:`SteamUnifiedMessages.get`)
            or method name (e.g. ``Player.GetGameBadgeLevels#1``)
        :type message: :class:`str`, proto message instance
        :param params: message parameters
        :type params: :class:`dict`
        :return: ``jobid`` event identifier
        :rtype: :class:`str`

        Listen for ``jobid`` on this object to catch the response.

        .. note::
            If you listen for ``jobid`` on the client instance you will get the encapsulated message
        """
        if isinstance(message, str):
            message = self.get(message)
        if message not in self._data:
            raise ValueError("Supplied message seems to be invalid. Did you use 'get' method?")

        if params:
            for k, v in params.items():
                if isinstance(v, list):
                    getattr(message, k).extend(v)
                else:
                    setattr(message, k, v)

        capsule = MsgProto(EMsg.ClientServiceMethod)
        capsule.body.method_name = self._data[message]
        capsule.body.serialized_method = message.SerializeToString()

        return self._steam.send_job(capsule)

    def send_and_wait(self, message, params=None, timeout=None, raises=False):
        """Send service method request and wait for response

        :param message:
            proto message instance (use :meth:`SteamUnifiedMessages.get`)
            or method name (e.g. ``Player.GetGameBadgeLevels#1``)
        :type message: :class:`str`, proto message instance
        :param params: message parameters
        :type params: :class:`dict`
        :param timeout: (optional) seconds to wait
        :type timeout: :class:`int`
        :param raises: (optional) On timeout if :class:`False` return :class:`None`, else raise :class:`gevent.Timeout`
        :type raises: :class:`bool`
        :return: response proto message instance
        :rtype: proto message, :class:`None`
        :raises: ``gevent.Timeout``
        """
        job_id = self.send(message, params)
        resp = self.wait_event(job_id, timeout, raises=raises)
        if resp is None and not raises:
            return None
        else:
            return resp[0]


class SteamLeaderboard(object):
    """.. versionadded:: 0.8.2

    Steam leaderboard object.
    Generated via :meth:`Misc.get_leaderboard()`
    Works more or less like a :class:`list` to access entries.

    .. note::
        Each slice will produce a message to steam.
        Steam and protobufs might not like large slices.
        Avoid accessing individual entries by index and instead use iteration or well sized slices.

    Example usage:

    .. code:: python

        lb = client.get_leaderboard(...)

        print len(lb)

        for entry in lb[:100]:  # top 100
            pass
    """
    app_id = 0
    name = ''  #: leaderboard name
    id = 0 #: leaderboard id
    entry_count = 0
    sort_method = ELeaderboardSortMethod.NONE      #: :class:`steam.enums.common.ELeaderboardSortMethod`
    display_type = ELeaderboardDisplayType.NONE    #: :class:`steam.enums.common.ELeaderboardDisplayType`
    data_request = ELeaderboardDataRequest.Global  #: :class:`steam.enums.common.ELeaderboardDataRequest`

    def __init__(self, steam, app_id, name, data):
        self._steam = steam
        self.app_id = app_id

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

    def get_entries(self, start=0, end=0, data_request=ELeaderboardDataRequest.Global):
        """Get leaderboard entries.

        :param start: start entry, not index (e.g. rank 1 is `start=1`)
        :type start: :class:`int`
        :param end: end entry, not index (e.g. only one entry then `start=1,end=1`)
        :type end: :class:`int`
        :param data_request: data being requested
        :type data_request: :class:`steam.enums.common.ELeaderboardDataRequest`
        :return: a list of entries, see `CMsgClientLBSGetLBEntriesResponse`
        :rtype: :class:`list`
        :raises: :class:`LookupError` on message timeout or error
        """
        message = MsgProto(EMsg.ClientLBSGetLBEntries)
        message.body.app_id = self.app_id
        message.body.leaderboard_id = self.id
        message.body.range_start = start
        message.body.range_end = end
        message.body.leaderboard_data_request = data_request

        resp = self._steam.send_job_and_wait(message, timeout=15)

        if not resp:
            raise LookupError("Didn't receive response within 15seconds :(")
        if resp.eresult != EResult.OK:
            raise LookupError(EResult(resp.eresult))

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
        else:
            start, stop, step = x, x + 1, 1

        if start >= stop: return []

        entries = self.get_entries(start+1, stop, self.data_request)

        return [entries[i] for i in _range(0, len(entries), step)]

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
            with ConstantRateLimit(times, seconds, use_gevent=True) as r:
                for entries in chunks(self, chunk_size):
                    if not entries:
                        raise StopIteration
                    for entry in entries:
                        yield entry
                    r.wait()
        return entry_generator()

    def __iter__(self):
        return self.get_iter(1, 1, 2000)
