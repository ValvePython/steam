"""
Implementation of Steam client based on ``gevent``

Events
^^^^^^

 | ``connected`` - when successful connection with a CM server is established
 | ``disconnected`` - when connection is lost
 | ``reconnect`` - when connect attempt is delayed, `delay` argument gives the delay in seconds
 | ``channel_secured`` - after channel encryption is complete, client can attempt to login now
 | ``error`` - after login failure
 | ``auth_code_required`` - either email code or 2FA code is needed for login
 | ``logged_on`` - after successful login, client can send messages
 | ``new_login_key`` - after new login key has been received and acknowledged
 | :class:`.EMsg` - all messages are emitted with their :class:`.EMsg` number


.. note::
    Mixins can emitter additional events. See their docs pages for details.

.. note::
    Additional features are located in separate submodules. All functionality from :mod:`.builtins` is inherited by default.

.. note::
    Optional features are available as :mod:`.mixins`. This allows the client to remain light yet flexible.

"""
import os
import json
from time import time
from io import open
import logging
import gevent
import gevent.monkey
gevent.monkey.patch_socket()
gevent.monkey.patch_ssl()

from steam.core.crypto import sha1_hash
from eventemitter import EventEmitter
from steam.enums.emsg import EMsg
from steam.enums import EResult, EOSType, EPersonaState
from steam.core.msg import MsgProto
from steam.core.cm import CMClient
from steam import SteamID
from steam.client.builtins import BuiltinBase
from steam.util import ip_from_int


class SteamClient(CMClient, BuiltinBase):
    _cm_servers_timestamp = None       # used to decide when to update CM list on disk
    _reconnect_backoff_c = 0
    current_jobid = 0
    credential_location = None         #: location for sentry
    username = None                    #: username when logged on
    login_key = None                   #: can be used for subsequent logins (no 2FA code will be required)

    def __init__(self):
        CMClient.__init__(self)

        self._LOG = logging.getLogger("SteamClient")
        # register listners
        self.on(None, self._handle_jobs)
        self.on("disconnected", self._handle_disconnect)
        self.on("reconnect", self._handle_disconnect)
        self.on(EMsg.ClientNewLoginKey, self._handle_login_key)
        self.on(EMsg.ClientUpdateMachineAuth, self._handle_update_machine_auth)

        #: indicates logged on status. Listen to ``logged_on`` when change to ``True``
        self.logged_on = False

        BuiltinBase.__init__(self)

    def __repr__(self):
        return "<%s(%s) %s>" % (self.__class__.__name__,
                              repr(self.current_server_addr),
                              'online' if self.connected else 'offline',
                              )

    def set_credential_location(self, path):
        """
        Sets folder location for sentry files

        Needs to be set explicitly for sentries to be created.
        """
        self.credential_location = path

    def connect(self, *args, **kwargs):
        """Attempt to establish connection, see :meth:`.CMClient.connect`"""
        self._bootstrap_cm_list_from_file()
        CMClient.connect(self, *args, **kwargs)

    def disconnect(self, *args, **kwargs):
        """Close connection, see :meth:`.CMClient.disconnect`"""
        self.logged_on = False
        CMClient.disconnect(self, *args, **kwargs)

    def _bootstrap_cm_list_from_file(self):
        if not self.credential_location or self._cm_servers_timestamp is not None: return

        filepath = os.path.join(self.credential_location, 'cm_servers.json')
        if not os.path.isfile(filepath): return

        self._LOG.debug("Reading CM servers from %s" % repr(filepath))
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
        except IOError as e:
            self._LOG.error("load %s: %s" % (repr(filepath), str(e)))
            return

        self.cm_servers.clear()
        self.cm_servers.merge_list(data['servers'])
        self._cm_servers_timestamp = int(data['timestamp'])

    def _handle_cm_list(self, msg):
        if self._cm_servers_timestamp is None:
            self.cm_servers.clear()
            self._cm_servers_timestamp = int(time())

        CMClient._handle_cm_list(self, msg)  # just merges the list

        if self.credential_location:
            filepath = os.path.join(self.credential_location, 'cm_servers.json')

            if not os.path.exists(filepath) or time() - (3600*24) > self._cm_servers_timestamp:
                data = {
                    'timestamp': self._cm_servers_timestamp,
                    'servers': list(zip(map(ip_from_int, msg.body.cm_addresses), msg.body.cm_ports)),
                }
                try:
                    with open(filepath, 'wb') as f:
                        f.write(json.dumps(data, indent=True).encode('ascii'))
                    self._LOG.debug("Saved CM servers to %s" % repr(filepath))
                except IOError as e:
                    self._LOG.error("saving %s: %s" % (filepath, str(e)))

    def _handle_jobs(self, event, *args):
        if isinstance(event, EMsg):
            message = args[0]

            if message.proto:
                jobid = message.header.jobid_target
            else:
                jobid = message.header.targetJobID

            if jobid not in (-1, 18446744073709551615):
                self.emit("job_%d" % jobid, *args)

    def _handle_disconnect(self, *args):
        self.logged_on = False
        self.current_jobid = 0

    def _handle_logon(self, msg):
        CMClient._handle_logon(self, msg)

        result = EResult(msg.body.eresult)

        if result == EResult.OK:
            self._reconnect_backoff_c = 0
            self.logged_on = True
            self.set_persona(EPersonaState.Online)
            self.emit("logged_on")
            return

        # CM kills the connection on error anyway
        self.disconnect()

        if result in (EResult.AccountLogonDenied,
                      EResult.InvalidLoginAuthCode,
                      EResult.AccountLoginDeniedNeedTwoFactor,
                      EResult.TwoFactorCodeMismatch,
                      ):

            is_2fa = (result in (EResult.AccountLoginDeniedNeedTwoFactor,
                                 EResult.TwoFactorCodeMismatch,
                                 ))

            if is_2fa:
                code_mismatch = (result == EResult.TwoFactorCodeMismatch)
            else:
                code_mismatch = (result == EResult.InvalidLoginAuthCode)

            self.emit("auth_code_required", is_2fa, code_mismatch)

    def _handle_login_key(self, message):
        resp = MsgProto(EMsg.ClientNewLoginKeyAccepted)
        resp.body.unique_id = message.body.unique_id

        if self.logged_on:
            self.send(resp)
            gevent.idle()
            self.login_key = message.body.login_key
            self.emit("new_login_key")

    def _handle_update_machine_auth(self, message):
        ok = self.store_sentry(self.username, message.body.bytes)

        if ok:
            resp = MsgProto(EMsg.ClientUpdateMachineAuthResponse)

            resp.header.jobid_target = message.header.jobid_source

            resp.body.filename = message.body.filename
            resp.body.eresult = EResult.OK
            resp.body.sha_file = sha1_hash(message.body.bytes)
            resp.body.getlasterror = 0
            resp.body.offset = message.body.offset
            resp.body.cubwrote = message.body.cubtowrite

            self.send(resp)

    def reconnect(self, maxdelay=30, retry=0):
        """Implements explonential backoff delay before attempting to connect.
        It is otherwise identical to calling :meth:`.CMClient.connect`.
        The delay is reset upon a successful login.

        :param maxdelay: maximum delay in seconds before connect (0-120s)
        :type maxdelay: :class:`int`
        :param retry: see :meth:`.CMClient.connect`
        :type retry: :class:`int`
        :return: successful connection
        :rtype: :class:`bool`
        """
        delay_seconds = 2**self._reconnect_backoff_c - 1

        if delay_seconds < maxdelay:
            self._reconnect_backoff_c = min(7, self._reconnect_backoff_c + 1)

        return self.connect(delay=delay_seconds, retry=retry)

    def send(self, message):
        """
        Send a message to CM

        :param message: a message instance
        :type message: :class:`.Msg`, :class:`.MsgProto`
        """
        if not self.connected:
            raise RuntimeError("Cannot send message while not connected")
        CMClient.send(self, message)

    def send_job(self, message):
        """
        Send a message as a job

        .. note::
            Not all messages are jobs, you'll have to find out which are which

        :param message: a message instance
        :type message: :class:`.Msg`, :class:`.MsgProto`
        :return: ``jobid`` event identifier
        :rtype: :class:`str`

        To catch the response just listen for the ``jobid`` event.

        .. code:: python

            jobid = steamclient.send_job(my_message)

            resp = steamclient.wait_event(jobid, timeout=15)
            if resp:
                (message,) = resp

            @steamclient.once(jobid)
            def handle_response(message):
                pass

        """
        jobid = self.current_jobid = (self.current_jobid + 1) % 4294967295

        if message.proto:
            message.header.jobid_source = jobid
        else:
            message.header.sourceJobID = jobid

        self.send(message)

        return "job_%d" % jobid

    def send_job_and_wait(self, message, timeout=None, raises=False):
        """
        Send a message as a job and wait for the response.

        .. note::
            Not all messages are jobs, you'll have to find out which are which

        :param message: a message instance
        :type message: :class:`.Msg`, :class:`.MsgProto`
        :param timeout: (optional) seconds to wait
        :type timeout: :class:`int`
        :param raises: (optional) On timeout if ``False`` return ``None``, else raise ``gevent.Timeout``
        :type raises: :class:`bool`
        :return: response proto message
        :rtype: :class:`.Msg`, :class:`.MsgProto`
        :raises: ``gevent.Timeout``
        """
        job_id = self.send_job(message)
        response = self.wait_event(job_id, timeout, raises=raises)
        if response is None:
            return None
        return response[0].body

    def send_message_and_wait(self, message, response_emsg, timeout=None, raises=False):
        """
        Send a message to CM and wait for a defined answer.

        :param message: a message instance
        :type message: :class:`.Msg`, :class:`.MsgProto`
        :param response_emsg: emsg to wait for
        :type response_emsg: :class:`.EMsg`,:class:`int`
        :param timeout: (optional) seconds to wait
        :type timeout: :class:`int`
        :param raises: (optional) On timeout if ``False`` return ``None``, else raise ``gevent.Timeout``
        :type raises: :class:`bool`
        :return: response proto message
        :rtype: :class:`.Msg`, :class:`.MsgProto`
        :raises: ``gevent.Timeout``
        """
        self.send(message)
        response = self.wait_event(response_emsg, timeout, raises=raises)
        if response is None:
            return None
        return response[0].body

    def _get_sentry_path(self, username):
        if self.credential_location is not None:
            return os.path.join(self.credential_location,
                                "%s_sentry.bin" % username
                                 )
        return None

    def get_sentry(self, username):
        """
        Returns contents of sentry file for the given username

        .. note::
            returns ``None`` if :attr:`credential_location` is not set, or file is not found/inaccessible

        :param username: username
        :type username: :class:`str`
        :return: sentry file contents, or ``None``
        :rtype: :class:`bytes`, :class:`None`
        """
        filepath = self._get_sentry_path(username)

        if filepath and os.path.isfile(filepath):
            try:
                with open(filepath, 'rb') as f:
                    return f.read()
            except IOError as e:
                self._LOG.error("get_sentry: %s" % str(e))

        return None

    def store_sentry(self, username, sentry_bytes):
        """
        Store sentry bytes under a username

        :param username: username
        :type username: :class:`str`
        :return: Whenver the operation succeed
        :rtype: :class:`bool`
        """
        filepath = self._get_sentry_path(username)
        if filepath:
            try:
                with open(filepath, 'wb') as f:
                    f.write(sentry_bytes)
                return True
            except IOError as e:
                self._LOG.error("store_sentry: %s" % str(e))

        return False

    def _pre_login(self):
        if self.logged_on:
            self._LOG.debug("Trying to login while logged on???")
            raise RuntimeError("Already logged on")

        if not self.connected:
            self.connect()

        if not self.channel_secured:
            self.wait_event("channel_secured")

    def login(self, username, password='', login_key=None, auth_code=None, two_factor_code=None):
        """
        Login as a specific user

        :param username: username
        :type username: :class:`str`
        :param password: password
        :type password: :class:`str`
        :param login_key: login key, instead of password
        :type login_key: :class:`str`
        :param auth_code: email authentication code
        :type auth_code: :class:`str`
        :param two_factor_code: 2FA authentication code
        :type two_factor_code: :class:`str`

        .. note::
            Failure to login will result in the server dropping the connection, ``error`` event is fired

        ``auth_code_required`` event is fired when 2FA or Email code is needed.
        Here is example code of how to handle the situation.

        .. code:: python

            @steamclient.on('auth_code_required')
            def auth_code_prompt(is_2fa, code_mismatch):
                if is_2fa:
                    code = raw_input("Enter 2FA Code: ")
                    steamclient.login(username, password, two_factor_code=code)
                else:
                    code = raw_input("Enter Email Code: ")
                    steamclient.login(username, password, auth_code=code)

        Codes are required every time a user logins if sentry is not setup.
        See :meth:`set_credential_location`
        """
        self._LOG.debug("Attempting login")

        self._pre_login()

        self.username = username

        message = MsgProto(EMsg.ClientLogon)
        message.header.steamid = SteamID(type='Individual', universe='Public')
        message.body.protocol_version = 65579
        message.body.client_package_version = 1771
        message.body.client_os_type = EOSType.Win10
        message.body.client_language = "english"
        message.body.should_remember_password = True

        message.body.account_name = username

        if login_key:
            message.body.login_key = login_key
        else:
            message.body.password = password

        sentry = self.get_sentry(username)
        if sentry is None:
            message.body.eresult_sentryfile = EResult.FileNotFound
        else:
            message.body.eresult_sentryfile = EResult.OK
            message.body.sha_sentryfile = sha1_hash(sentry)

        if auth_code:
            message.body.auth_code = auth_code
        if two_factor_code:
            message.body.two_factor_code = two_factor_code

        self.send(message)

    def anonymous_login(self):
        """
        Login as anonymous user
        """
        self._LOG.debug("Attempting Anonymous login")

        self._pre_login()

        self.username = None
        self.login_key = None

        message = MsgProto(EMsg.ClientLogon)
        message.header.steamid = SteamID(type='AnonUser', universe='Public')
        message.body.protocol_version = 65579
        self.send(message)

    def logout(self):
        """
        Logout from steam. Doesn't nothing if not logged on.

        .. note::
            The server will drop the connection immediatelly upon logout.
        """
        if self.logged_on:
            self.logged_on = False
            self.send(MsgProto(EMsg.ClientLogOff))
            self.wait_event('disconnected')

    def run_forever(self):
        """
        Transfer control the gevent event loop

        This is useful when the application is setup and ment to run for a long time
        """
        while True:
            gevent.sleep(300)
