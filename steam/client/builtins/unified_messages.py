"""
:class:`SteamUnifiedMessages` provides a simply API to send and receive unified messages.

Example code:

.. code:: python

    # the easy way
    response = client.unified_messages.send_and_wait('Player.GetGameBadgeLevels#1', {
        'property': 1,
        'something': 'value',
        })

    # the other way
    jobid = client.unified_message.send('Player.GetGameBadgeLevels#1', {'something': 1})
    response, = client.unified_message.wait_event(jobid)

    # i know what im doing, alright?
    message = client.unified_message.get('Player.GetGameBadgeLevels#1')
    message.something = 1
    response = client.unified_message.send_and_wait(message)
"""
import logging
from eventemitter import EventEmitter
from steam.core.msg import MsgProto, get_um
from steam.enums import EResult
from steam.enums.emsg import EMsg
from steam.util import WeakRefKeyDict, proto_fill_from_dict


class UnifiedMessages(object):
    def __init__(self, *args, **kwargs):
        super(UnifiedMessages, self).__init__(*args, **kwargs)

        name = "%s.unified_messages" % self.__class__.__name__
        self.unified_messages = SteamUnifiedMessages(self, name)  #: instance of :class:`SteamUnifiedMessages`


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
            self._LOG.error("Unable to find proto for %s" % repr(method_name))
            return

        if message.header.eresult != EResult.OK:
            self._LOG.error("%s (%s): %s" % (method_name, repr(EResult(message.header.eresult)),
                                             message.header.error_message))

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
            proto_fill_from_dict(message, params)

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
        :raises: :class:`gevent.Timeout`
        """
        job_id = self.send(message, params)
        resp = self.wait_event(job_id, timeout, raises=raises)
        if resp is None and not raises:
            return None
        else:
            return resp[0]
