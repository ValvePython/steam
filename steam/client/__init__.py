"""
Implementation of Steam client based on ``gevent``

.. note::
    Additional features are located in separate submodules. All functionality from :mod:`.builtins` is inherited by default.

.. note::
    Optional features are available as :mod:`.mixins`. This allows the client to remain light yet flexible.

"""
import gevent
import gevent.monkey
gevent.monkey.patch_socket()
gevent.monkey.patch_ssl()

import os
import json
from time import time
from io import open
from getpass import getpass
import logging
import six

from eventemitter import EventEmitter
from steam.enums import EResult, EOSType, EPersonaState
from steam.enums.emsg import EMsg
from steam.core.cm import CMClient
from steam.core.msg import MsgProto
from steam.core.crypto import sha1_hash
from steam.steamid import SteamID
from steam.exceptions import SteamError
from steam.client.builtins import BuiltinBase
from steam.util import ip_from_int, ip_to_int, proto_fill_from_dict

if six.PY2:
    _cli_input = raw_input
else:
    _cli_input = input


class SteamClient(CMClient, BuiltinBase):
    EVENT_LOGGED_ON = 'logged_on'
    """After successful login
    """
    EVENT_AUTH_CODE_REQUIRED = 'auth_code_required'
    """When either email or 2FA code is needed for login
    """
    EVENT_NEW_LOGIN_KEY = 'new_login_key'
    """After a new login key is accepted
    """

    _reconnect_backoff_c = 0
    current_jobid = 0
    credential_location = None         #: location for sentry
    username = None                    #: username when logged on
    login_key = None                   #: can be used for subsequent logins (no 2FA code will be required)
    chat_mode = 2                      #: chat mode (0=old chat, 2=new chat)

    def __init__(self):
        CMClient.__init__(self)

        self._LOG = logging.getLogger("SteamClient")
        # register listners
        self.on(self.EVENT_DISCONNECTED, self._handle_disconnect)
        self.on(self.EVENT_RECONNECT, self._handle_disconnect)
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
        return CMClient.connect(self, *args, **kwargs)

    def disconnect(self, *args, **kwargs):
        """Close connection, see :meth:`.CMClient.disconnect`"""
        self.logged_on = False
        CMClient.disconnect(self, *args, **kwargs)

    def _parse_message(self, message):
        result = CMClient._parse_message(self, message)

        if result is None:
            return

        emsg, msg = result

        # emit job events
        if msg.proto:
            jobid = msg.header.jobid_target
        else:
            jobid = msg.header.targetJobID

        if jobid not in (-1, 18446744073709551615):
            jobid = "job_%d" % jobid
            if msg.body is None and self.count_listeners(jobid):
                msg.parse()
            self.emit(jobid, msg)

        # emit UMs
        if emsg in (EMsg.ServiceMethod, EMsg.ServiceMethodResponse, EMsg.ServiceMethodSendToClient):
            if msg.body is None and self.count_listeners(msg.header.target_job_name):
                msg.parse()
            self.emit(msg.header.target_job_name, msg)

    def _bootstrap_cm_list_from_file(self):
        if not self.credential_location or self.cm_servers.last_updated > 0:
            return

        filepath = os.path.join(self.credential_location, 'cm_servers.json')

        if not os.path.isfile(filepath):
            return

        self._LOG.debug("Reading CM servers from %s" % repr(filepath))

        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
        except ValueError:
            self._LOG.error("Failed parsing %s", repr(filepath))
        except IOError as e:
            self._LOG.error("Failed reading %s (%s)", repr(filepath), str(e))
        else:
            self.cm_servers.clear()
            self.cm_servers.merge_list(data['servers'])
            self.cm_servers.last_updated = data.get('last_updated', 0)
            self.cm_servers.cell_id = data.get('cell_id', 0)

    def _handle_cm_list(self, msg):
        if (self.cm_servers.last_updated + 3600*24 > time()
           and self.cm_servers.cell_id != 0):
            return

        CMClient._handle_cm_list(self, msg)  # clear and merge

        if self.credential_location:
            filepath = os.path.join(self.credential_location, 'cm_servers.json')

            if os.path.exists(filepath):
                try:
                    with open(filepath, 'r') as f:
                        data = json.load(f)
                except ValueError:
                    self._LOG.error("Failed parsing %s", repr(filepath))
                except IOError as e:
                    self._LOG.error("Failed reading %s (%s)", repr(filepath), str(e))
                else:
                    if data.get('last_updated', 0) + 3600*24 > time():
                        return

                self._LOG.debug("Persisted CM server list is stale")

            data = {
                'cell_id': self.cm_servers.cell_id,
                'last_updated': self.cm_servers.last_updated,
                'servers': list(zip(map(ip_from_int, msg.body.cm_addresses), msg.body.cm_ports)),
            }
            try:
                with open(filepath, 'wb') as f:
                    f.write(json.dumps(data, indent=True).encode('ascii'))
                self._LOG.debug("Saved CM servers to %s" % repr(filepath))
            except IOError as e:
                self._LOG.error("saving %s: %s" % (filepath, str(e)))

    def _handle_disconnect(self, *args):
        self.logged_on = False
        self.current_jobid = 0

    def _handle_logon(self, msg):
        CMClient._handle_logon(self, msg)

        result = EResult(msg.body.eresult)

        if result == EResult.OK:
            self._reconnect_backoff_c = 0
            self.logged_on = True
            self.emit(self.EVENT_LOGGED_ON)
            return

        # CM kills the connection on error anyway
        self.disconnect()

        if result == EResult.InvalidPassword:
            self.login_key = None

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

            self.emit(self.EVENT_AUTH_CODE_REQUIRED, is_2fa, code_mismatch)

    def _handle_login_key(self, message):
        resp = MsgProto(EMsg.ClientNewLoginKeyAccepted)
        resp.body.unique_id = message.body.unique_id

        if self.logged_on:
            self.send(resp)
            self.idle()
            self.login_key = message.body.login_key
            self.emit(self.EVENT_NEW_LOGIN_KEY)

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

    def wait_msg(self, event, timeout=None, raises=None):
        """Wait for a message, similiar to :meth:`.wait_event`

        :param event: :class:`.EMsg` or job id
        :type  event: :class:`.EMsg` or :class:`str`
        :param timeout: seconds to wait before timeout
        :type  timeout: :class:`int`
        :param raises: On timeout when ``False`` returns :class:`None`, else raise :class:`gevent.Timeout`
        :type  raises: :class:`bool`
        :return: returns a message or :class:`None`
        :rtype: :class:`None`, or `proto message`
        :raises: ``gevent.Timeout``
        """
        resp = self.wait_event(event, timeout, raises)

        if resp is not None:
            return resp[0]

    def send(self, message, body_params=None):
        """
        Send a message to CM

        :param message: a message instance
        :type message: :class:`.Msg`, :class:`.MsgProto`
        :param body_params: a dict with params to the body (only :class:`.MsgProto`)
        :type body_params: dict
        """
        if not self.connected:
            self._LOG.debug("Trying to send message when not connected. (discarded)")
        else:
            if body_params and isinstance(message, MsgProto):
                proto_fill_from_dict(message.body, body_params)

            CMClient.send(self, message)

    def send_job(self, message, body_params=None):
        """
        Send a message as a job

        .. note::
            Not all messages are jobs, you'll have to find out which are which

        :param message: a message instance
        :type message: :class:`.Msg`, :class:`.MsgProto`
        :param body_params: a dict with params to the body (only :class:`.MsgProto`)
        :type body_params: dict
        :return: ``jobid`` event identifier
        :rtype: :class:`str`

        To catch the response just listen for the ``jobid`` event.

        .. code:: python

            jobid = steamclient.send_job(my_message)

            resp = steamclient.wait_event(jobid, timeout=15)
            if resp:
                (message,) = resp

        """
        jobid = self.current_jobid = ((self.current_jobid + 1) % 10000) or 1
        self.remove_all_listeners('job_%d' % jobid)

        if message.proto:
            message.header.jobid_source = jobid
        else:
            message.header.sourceJobID = jobid

        self.send(message, body_params)

        return "job_%d" % jobid

    def send_job_and_wait(self, message, body_params=None, timeout=None, raises=False):
        """
        Send a message as a job and wait for the response.

        .. note::
            Not all messages are jobs, you'll have to find out which are which

        :param message: a message instance
        :type message: :class:`.Msg`, :class:`.MsgProto`
        :param body_params: a dict with params to the body (only :class:`.MsgProto`)
        :type body_params: dict
        :param timeout: (optional) seconds to wait
        :type timeout: :class:`int`
        :param raises: (optional) On timeout if ``False`` return ``None``, else raise ``gevent.Timeout``
        :type raises: :class:`bool`
        :return: response proto message
        :rtype: :class:`.Msg`, :class:`.MsgProto`
        :raises: ``gevent.Timeout``
        """
        job_id = self.send_job(message, body_params)
        response = self.wait_event(job_id, timeout, raises=raises)
        if response is None:
            return None
        return response[0].body

    def send_message_and_wait(self, message, response_emsg, body_params=None, timeout=None, raises=False):
        """
        Send a message to CM and wait for a defined answer.

        :param message: a message instance
        :type message: :class:`.Msg`, :class:`.MsgProto`
        :param response_emsg: emsg to wait for
        :type response_emsg: :class:`.EMsg`,:class:`int`
        :param body_params: a dict with params to the body (only :class:`.MsgProto`)
        :type body_params: dict
        :param timeout: (optional) seconds to wait
        :type timeout: :class:`int`
        :param raises: (optional) On timeout if ``False`` return ``None``, else raise ``gevent.Timeout``
        :type raises: :class:`bool`
        :return: response proto message
        :rtype: :class:`.Msg`, :class:`.MsgProto`
        :raises: ``gevent.Timeout``
        """
        self.send(message, body_params)
        response = self.wait_event(response_emsg, timeout, raises=raises)
        if response is None:
            return None
        return response[0].body

    def _get_sentry_path(self, username):
        if self.credential_location:
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

        if not self.connected and not self._connecting:
            if not self.connect():
                return EResult.Fail

        if not self.channel_secured:
            resp = self.wait_event(self.EVENT_CHANNEL_SECURED, timeout=10)

            # some CMs will not send hello
            if resp is None:
                if self.connected:
                    self.wait_event(self.EVENT_DISCONNECTED)
                return EResult.TryAnotherCM

        return EResult.OK

    @property
    def relogin_available(self):
        """``True`` when the client has the nessesary data for :meth:`relogin`"""
        return bool(self.username) and bool(self.login_key)

    def relogin(self):
        """Login without needing credentials, essentially remember password.
        The :attr:`login_key` is acquired after successful login and it will be
        automatically acknowledged. Listen for the ``new_login_key`` event.
        After that the client can relogin using this method.

        .. note::
            Only works when :attr:`relogin_available` is ``True``.

        .. code:: python

            if client.relogin_available: client.relogin()
            else:
                client.login(user, pass)
        """
        if self.relogin_available:
            self.login(self.username, '', self.login_key)

    def login(self, username, password='', login_key=None, auth_code=None, two_factor_code=None, login_id=None):
        """Login as a specific user

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
        :param login_id: number used for identifying logon session
        :type login_id: :class:`int`
        :return: logon result, see `CMsgClientLogonResponse.eresult <https://github.com/ValvePython/steam/blob/513c68ca081dc9409df932ad86c66100164380a6/protobufs/steammessages_clientserver.proto#L95-L118>`_
        :rtype: :class:`.EResult`

        .. note::
            Failure to login will result in the server dropping the connection, ``error`` event is fired

        ``auth_code_required`` event is fired when 2FA or Email code is needed.
        Here is example code of how to handle the situation.

        .. code:: python

            @steamclient.on(steamclient.EVENT_AUTH_CODE_REQUIRED)
            def auth_code_prompt(is_2fa, code_mismatch):
                if is_2fa:
                    code = input("Enter 2FA Code: ")
                    steamclient.login(username, password, two_factor_code=code)
                else:
                    code = input("Enter Email Code: ")
                    steamclient.login(username, password, auth_code=code)

        Codes are required every time a user logins if sentry is not setup.
        See :meth:`set_credential_location`
        """
        self._LOG.debug("Attempting login")

        eresult = self._pre_login()

        if eresult != EResult.OK:
            return eresult

        self.username = username

        message = MsgProto(EMsg.ClientLogon)
        message.header.steamid = SteamID(type='Individual', universe='Public')
        message.body.protocol_version = 65580
        message.body.client_package_version = 1561159470
        message.body.client_os_type = EOSType.Windows10
        message.body.client_language = "english"
        message.body.should_remember_password = True
        message.body.supports_rate_limit_response = True
        message.body.chat_mode = self.chat_mode

        if login_id is None:
            message.body.obfuscated_private_ip.v4 = ip_to_int(self.connection.local_address) ^ 0xF00DBAAD
        else:
            message.body.obfuscated_private_ip.v4 = login_id

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

        resp = self.wait_msg(EMsg.ClientLogOnResponse, timeout=30)

        if resp and resp.body.eresult == EResult.OK:
            self.sleep(0.5)

        return EResult(resp.body.eresult) if resp else EResult.Fail

    def anonymous_login(self):
        """Login as anonymous user

        :return: logon result, see `CMsgClientLogonResponse.eresult <https://github.com/ValvePython/steam/blob/513c68ca081dc9409df932ad86c66100164380a6/protobufs/steammessages_clientserver.proto#L95-L118>`_
        :rtype: :class:`.EResult`
        """
        self._LOG.debug("Attempting Anonymous login")

        eresult = self._pre_login()

        if eresult != EResult.OK:
            return eresult

        self.username = None
        self.login_key = None

        message = MsgProto(EMsg.ClientLogon)
        message.header.steamid = SteamID(type='AnonUser', universe='Public')
        message.body.client_package_version = 1561159470
        message.body.protocol_version = 65580
        self.send(message)

        resp = self.wait_msg(EMsg.ClientLogOnResponse, timeout=30)
        return EResult(resp.body.eresult) if resp else EResult.Fail

    def logout(self):
        """
        Logout from steam. Doesn't nothing if not logged on.

        .. note::
            The server will drop the connection immediatelly upon logout.
        """
        if self.logged_on:
            self.logged_on = False
            self.send(MsgProto(EMsg.ClientLogOff))
            try:
                self.wait_event(self.EVENT_DISCONNECTED, timeout=5, raises=True)
            except:
                self.disconnect()
            self.idle()

    def run_forever(self):
        """
        Transfer control the gevent event loop

        This is useful when the application is setup and ment to run for a long time
        """
        while True:
            self.sleep(300)

    def cli_login(self, username='', password=''):
        """Generates CLI prompts to complete the login process

        :param username: optionally provide username
        :type  username: :class:`str`
        :param password: optionally provide password
        :type  password: :class:`str`
        :return: logon result, see `CMsgClientLogonResponse.eresult <https://github.com/ValvePython/steam/blob/513c68ca081dc9409df932ad86c66100164380a6/protobufs/steammessages_clientserver.proto#L95-L118>`_
        :rtype: :class:`.EResult`

        Example console output after calling :meth:`cli_login`

        .. code:: python

            In [5]: client.cli_login()
            Steam username: myusername
            Password:
            Steam is down. Keep retrying? [y/n]: y
            Invalid password for 'myusername'. Enter password:
            Enter email code: 123
            Incorrect code. Enter email code: K6VKF
            Out[5]: <EResult.OK: 1>
        """
        if not username:
            username = _cli_input("Username: ")
        if not password:
            password = getpass()

        auth_code = two_factor_code = None
        prompt_for_unavailable = True

        result = self.login(username, password)

        while result in (EResult.AccountLogonDenied, EResult.InvalidLoginAuthCode,
                         EResult.AccountLoginDeniedNeedTwoFactor, EResult.TwoFactorCodeMismatch,
                         EResult.TryAnotherCM, EResult.ServiceUnavailable,
                         EResult.InvalidPassword,
                         ):
            self.sleep(0.1)

            if result == EResult.InvalidPassword:
                password = getpass("Invalid password for %s. Enter password: " % repr(username))

            elif result in (EResult.AccountLogonDenied, EResult.InvalidLoginAuthCode):
                prompt = ("Enter email code: " if result == EResult.AccountLogonDenied else
                          "Incorrect code. Enter email code: ")
                auth_code, two_factor_code = _cli_input(prompt), None

            elif result in (EResult.AccountLoginDeniedNeedTwoFactor, EResult.TwoFactorCodeMismatch):
                prompt = ("Enter 2FA code: " if result == EResult.AccountLoginDeniedNeedTwoFactor else
                          "Incorrect code. Enter 2FA code: ")
                auth_code, two_factor_code = None, _cli_input(prompt)

            elif result in (EResult.TryAnotherCM, EResult.ServiceUnavailable):
                if prompt_for_unavailable and result == EResult.ServiceUnavailable:
                    while True:
                        answer = _cli_input("Steam is down. Keep retrying? [y/n]: ").lower()
                        if answer in 'yn': break

                    prompt_for_unavailable = False
                    if answer == 'n': break

                self.reconnect(maxdelay=15)  # implements reconnect throttling

            result = self.login(username, password, None, auth_code, two_factor_code)

        return result
