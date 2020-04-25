"""
Methods to call service methods, also known as unified messages

Example code:

.. code:: python

    # the easy way
    response = client.send_um_and_wait('Player.GetGameBadgeLevels#1', {
        'property': 1,
        'something': 'value',
        })

    print(response.body)

    # the other way
    jobid = client.send_um('Player.GetGameBadgeLevels#1', {'something': 1})
    response = client.wait_event(jobid)

The backend might error out, but we still get response. Here is how to check for error:

.. code:: python

    if response.header.eresult != EResult.OK:
        print(response.header.error_message)

"""
from steam.core.msg import MsgProto, get_um
from steam.enums.emsg import EMsg
from steam.utils.proto import proto_fill_from_dict


class UnifiedMessages(object):
    def __init__(self, *args, **kwargs):
        super(UnifiedMessages, self).__init__(*args, **kwargs)

    def send_um(self, method_name, params=None):
        """Send service method request

        :param method_name: method name (e.g. ``Player.GetGameBadgeLevels#1``)
        :type  method_name: :class:`str`
        :param params: message parameters
        :type  params: :class:`dict`
        :return: ``job_id`` identifier
        :rtype: :class:`str`

        Listen for ``jobid`` on this object to catch the response.
        """
        proto = get_um(method_name)

        if proto is None:
            raise ValueError("Failed to find method named: %s" % method_name)

        message = MsgProto(EMsg.ServiceMethodCallFromClient)
        message.header.target_job_name = method_name
        message.body = proto()

        if params:
            proto_fill_from_dict(message.body, params)

        return self.send_job(message)

    def send_um_and_wait(self, method_name, params=None, timeout=10, raises=False):
        """Send service method request and wait for response

        :param method_name: method name (e.g. ``Player.GetGameBadgeLevels#1``)
        :type  method_name: :class:`str`
        :param params: message parameters
        :type  params: :class:`dict`
        :param timeout: (optional) seconds to wait
        :type  timeout: :class:`int`
        :param raises: (optional) On timeout if :class:`False` return :class:`None`, else raise :class:`gevent.Timeout`
        :type  raises: :class:`bool`
        :return: response message
        :rtype: proto message instance
        :raises: :class:`gevent.Timeout`
        """
        job_id = self.send_um(method_name, params)
        return self.wait_msg(job_id, timeout, raises=raises)
