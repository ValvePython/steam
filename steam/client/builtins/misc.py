"""
Various features that don't have a category
"""
import logging
from eventemitter import EventEmitter
from steam.core.msg import MsgProto, get_um
from steam.enums.emsg import EMsg
from steam.util import WeakRefKeyDict

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


class SteamUnifiedMessages(EventEmitter):
    """Simple API for send/recv of unified messages

    Incoming messages are emitted as events once with their ``jobid``
    and once with their method name (e.g. ``Player.GetGameBadgeLevels#1``)
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
        :return: proto message instance, or ``None`` if not found
        """
        proto = get_um(method_name)
        if proto is None:
            return None
        message = proto()
        self._data[message] = method_name
        return message

    def send(self, message):
        """Send service method request

        :param message: proto message instance (use :meth:`get`)
        :return: ``jobid`` event identifier
        :rtype: :class:`str`

        Listen for ``jobid`` on this object to catch the response.

        .. note::
            If you listen for ``jobid`` on the client instance you will get the encapsulated message
        """
        if message not in self._data:
            raise ValueError("Supplied message seems to be invalid. Did you use 'get' method?")

        capsule = MsgProto(EMsg.ClientServiceMethod)
        capsule.body.method_name = self._data[message]
        capsule.body.serialized_method = message.SerializeToString()

        return self._steam.send_job(capsule)

    def send_and_wait(self, message, timeout=None, raises=False):
        """Send service method request and wait for response

        :param message: proto message instance (use :meth:`get`)
        :param timeout: (optional) seconds to wait
        :type timeout: :class:`int`
        :param raises: (optional) On timeout if ``False`` return ``None``, else raise ``gevent.Timeout``
        :type raises: :class:`bool`
        :return: response proto message instance
        :rtype: proto message, :class:`None`
        :raises: ``gevent.Timeout``
        """
        job_id = self.send(message)
        resp = self.wait_event(job_id, timeout, raises=raises)
        if resp is None and not raises:
            return None
        else:
            return resp[0]
