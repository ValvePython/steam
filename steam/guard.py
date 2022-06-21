"""
This submodule contains various functionality related to Steam Guard.

:class:`SteamAuthenticator` provides methods for genereating codes
and enabling 2FA on a Steam account. Operations managing the authenticator
on an account require an instance of either :class:`.MobileWebAuth` or
:class:`.SteamClient`. The instance needs to be logged in.

Adding an authenticator

.. code:: python

    wa = MobileWebAuth('steamuser')
    wa.cli_login()

    sa = SteamAuthenticator(backend=wa)
    sa.add()    # SMS code will be send to the account's phone number
    sa.secrets  # dict with authenticator secrets (SAVE THEM!!)

    # save the secrets, for example to a file
    json.dump(sa.secrets, open('./mysecrets.json', 'w'))

    # HINT: You can stop here and add authenticator on your phone.
    #       The secrets will be the same, and you will be able to
    #       both use your phone and SteamAuthenticator.

    sa.finalize('SMS CODE')  # activate the authenticator
    sa.get_code()  # generate 2FA code for login
    sa.remove()  # removes the authenticator from the account

.. warning::
    Before you finalize the authenticator, make sure to save your secrets.
    Otherwise you will lose access to the account.

Once authenticator is enabled all you need is the secrets to generate codes.

.. code:: python

    secrets = json.load(open('./mysecrets.json'))

    sa = SteamAuthenticator(secrets)
    sa.get_code()

You can obtain the authenticator secrets from an Android device using
:func:`extract_secrets_from_android_rooted`. See the function docstring for
details on what is required for it to work.

Format of ``secrets.json`` file:

.. code:: json

    {
        "account_name": "<username>",               # account username
        "identity_secret": "<base64 encoded>",      # unknown
        "revocation_code": "R51234",                # revocation code
        "secret_1": "<base54 encoded>",             # unknown
        "serial_number": "1111222333344445555",     # serial number
        "server_time": "1600000000",                # creation timestamp
        "shared_secret": "<base65 encoded>",        # secret used for code generation
        "status": 1,                                # status, 1 = token active
        "token_gid": "a1a1a1a1a1a1a1a1",            # token gid
        "uri": "otpauth://totp/Steam:<username>?secret=<base32 encoded shared seceret>&issuer=Steam"
    }
"""
import json
import subprocess
import struct
import requests
from base64 import b64decode, b64encode
from binascii import hexlify
from time import time
from steam import webapi
from steam.enums import ETwoFactorTokenType
from steam.steamid import SteamID
from steam.core.crypto import hmac_sha1, sha1_hash
from steam.enums.common import EResult
from steam.webauth import MobileWebAuth
from steam.utils.proto import proto_to_dict


class SteamAuthenticator(object):
    """Add/Remove authenticator from an account. Generate 2FA and confirmation codes."""
    _finalize_attempts = 5
    backend = None               #: instance of :class:`.MobileWebAuth` or :class:`.SteamClient`
    steam_time_offset = None     #: offset from steam server time
    align_time_every = 0         #: how often to align time with Steam (``0`` never, otherwise interval in seconds)
    _offset_last_check = 0
    secrets = None               #: :class:`dict` with authenticator secrets

    def __init__(self, secrets=None, backend=None):
        """
        :param secret: a dict of authenticator secrets
        :type  secret: dict
        :param backend: logged on session for steam user
        :type  backend: :class:`.MobileWebAuth`, :class:`.SteamClient`
        """
        self.secrets = secrets or {}
        self.backend = backend

    def __getattr__(self, key):
        if key not in self.secrets:
            raise AttributeError("No %s attribute" % repr(key))
        return self.secrets[key]

    def get_time(self):
        """
        :return: Steam aligned timestamp
        :rtype: int
        """
        if (self.steam_time_offset is None
           or (self.align_time_every and (time() - self._offset_last_check) > self.align_time_every)
           ):
            self.steam_time_offset = get_time_offset()

            if self.steam_time_offset is not None:
                self._offset_last_check = time()

        return int(time() + (self.steam_time_offset or 0))

    def get_code(self, timestamp=None):
        """
        :param timestamp: time to use for code generation
        :type timestamp: int
        :return: two factor code
        :rtype: str
        """
        return generate_twofactor_code_for_time(b64decode(self.shared_secret),
                                                self.get_time() if timestamp is None else timestamp)

    def get_confirmation_key(self, tag='', timestamp=None):
        """
        :param tag: see :func:`generate_confirmation_key` for this value
        :type tag: str
        :param timestamp: time to use for code generation
        :type timestamp: int
        :return: trade confirmation key
        :rtype: str
        """
        return generate_confirmation_key(b64decode(self.identity_secret), tag,
                                         self.get_time() if timestamp is None else timestamp)

    def _send_request(self, action, params):
        backend = self.backend

        if isinstance(backend, MobileWebAuth):
            if not backend.logged_on:
                raise SteamAuthenticatorError("MobileWebAuth instance not logged in")

            params['access_token'] = backend.oauth_token
            params['http_timeout'] = 10

            try:
                resp = webapi.post('ITwoFactorService', action, 1, params=params)
            except requests.exceptions.RequestException as exp:
                raise SteamAuthenticatorError("Error adding via WebAPI: %s" % str(exp))

            resp = resp['response']
        else:
            if not backend.logged_on:
                raise SteamAuthenticatorError("SteamClient instance not logged in")

            resp = backend.send_um_and_wait("TwoFactor.%s#1" % action,
                                            params, timeout=10)

            if resp is None:
                raise SteamAuthenticatorError("Failed. Request timeout")
            if resp.header.eresult != EResult.OK:
                raise SteamAuthenticatorError("Failed: %s (%s)" % (resp.header.error_message,
                                                                   repr(resp.header.eresult)))

            resp = proto_to_dict(resp.body)

            if action == 'AddAuthenticator':
                for key in ['shared_secret', 'identity_secret', 'secret_1']:
                    resp[key] = b64encode(resp[key]).decode('ascii')

        return resp

    def add(self):
        """Add authenticator to an account.
        The account's phone number will receive a SMS code required for :meth:`finalize`.

        :raises: :class:`SteamAuthenticatorError`
        """
        if not self.has_phone_number():
            raise SteamAuthenticatorError("Account doesn't have a verified phone number")

        resp = self._send_request('AddAuthenticator', {
            'steamid': self.backend.steam_id,
            'authenticator_time': int(time()),
            'authenticator_type': int(ETwoFactorTokenType.ValveMobileApp),
            'device_identifier': generate_device_id(self.backend.steam_id),
            'sms_phone_id': '1',
        })

        if resp['status'] != EResult.OK:
            raise SteamAuthenticatorError("Failed to add authenticator. Error: %s" % repr(EResult(resp['status'])))

        self.secrets = resp
        self.steam_time_offset = int(resp['server_time']) - time()

    def finalize(self, activation_code):
        """Finalize authenticator with received SMS code

        :param activation_code: SMS code
        :type activation_code: str
        :raises: :class:`SteamAuthenticatorError`
        """
        resp = self._send_request('FinalizeAddAuthenticator', {
            'steamid': self.backend.steam_id,
            'authenticator_time': int(time()),
            'authenticator_code': self.get_code(),
            'activation_code': activation_code,
        })

        if resp['status'] != EResult.TwoFactorActivationCodeMismatch and resp.get('want_more', False) and self._finalize_attempts:
            self.steam_time_offset += 30
            self._finalize_attempts -= 1
            self.finalize(activation_code)
            return
        elif not resp['success']:
            self._finalize_attempts = 5
            raise SteamAuthenticatorError("Failed to finalize authenticator. Error: %s" % repr(EResult(resp['status'])))

        self.steam_time_offset = int(resp['server_time']) - time()

    def remove(self, revocation_code=None):
        """Remove authenticator

        :param revocation_code: revocation code for account (e.g. R12345)
        :type  revocation_code: str

        .. note::
            After removing authenticator Steam Guard will be set to email codes

        .. warning::
            Doesn't work via :class:`.SteamClient`. Disabled by Valve

        :raises: :class:`SteamAuthenticatorError`
        """
        if not self.secrets:
            raise SteamAuthenticatorError("No authenticator secrets available?")
        if not isinstance(self.backend, MobileWebAuth):
            raise SteamAuthenticatorError("Only available via MobileWebAuth")

        resp = self._send_request('RemoveAuthenticator', {
            'steamid': self.backend.steam_id,
            'revocation_code': revocation_code if revocation_code else self.revocation_code,
            'steamguard_scheme': 1,
        })

        if not resp['success']:
            raise SteamAuthenticatorError("Failed to remove authenticator. (attempts remaining: %s)" % (
                resp['revocation_attempts_remaining'],
                ))

        self.secrets.clear()

    def status(self):
        """Fetch authenticator status for the account

        :raises: :class:`SteamAuthenticatorError`
        :return: dict with status parameters
        :rtype: dict
        """
        return self._send_request('QueryStatus', {'steamid': self.backend.steam_id})

    def create_emergency_codes(self, code=None):
        """Generate emergency codes

        :param code: SMS code
        :type code: str
        :raises: :class:`SteamAuthenticatorError`
        :return: list of codes
        :rtype: list

        .. note::
            A confirmation code is required to generate emergency codes and this method needs
            to be called twice as shown below.

        .. code:: python

            sa.create_emergency_codes()              # request a SMS code
            sa.create_emergency_codes(code='12345')  # creates emergency codes
        """
        if code:
            return self._send_request('createemergencycodes', {'code': code}).get('codes', [])
        else:
            self._send_request('createemergencycodes', {})
            return None

    def destroy_emergency_codes(self):
        """Destroy all emergency codes

        :raises: :class:`SteamAuthenticatorError`
        """
        self._send_request('DestroyEmergencyCodes', {'steamid': self.backend.steam_id})

    def _get_web_session(self):
        """
        :return: authenticated web session
        :rtype: :class:`requests.Session`
        :raises: :class:`RuntimeError` when session is unavailable
        """
        if isinstance(self.backend, MobileWebAuth):
            return self.backend.session
        else:
            if self.backend.logged_on:
                sess = self.backend.get_web_session()

                if sess is None:
                    raise RuntimeError("Failed to get a web session. Try again in a few minutes")
                else:
                    return sess
            else:
                raise RuntimeError("SteamClient instance is not connected")

    def add_phone_number(self, phone_number):
        """Add phone number to account

        Steps:

        1. Call :meth:`add_phone_number()` then check ``email_confirmation`` key in the response

           i. On ``True``, user needs to click link in email, then step 2
           ii. On ``False``, SMS code is sent,  go to step 3

        2. Confirm email via :meth:`confirm_email()`, SMS code is sent
        3. Finalize phone number with SMS code :meth:`confirm_phone_number(sms_code)`

        :param phone_number: phone number with country code
        :type  phone_number: :class:`str`
        :return: see example below
        :rtype: :class:`dict`

        .. code:: python

            {'success': True,
             'email_confirmation': True,
             'error_text': '',
             'fatal': False}
        """
        sess = self._get_web_session()

        try:
            resp = sess.post('https://steamcommunity.com/steamguard/phoneajax',
                             data={
                                 'op': 'add_phone_number',
                                 'arg': phone_number,
                                 'checkfortos': 0,
                                 'skipvoip': 0,
                                 'sessionid': sess.cookies.get('sessionid', domain='steamcommunity.com'),
                                 },
                             timeout=15).json()
        except:
            return {'success': False}

        return resp

    def confirm_email(self):
        """Confirm email confirmation. See :meth:`add_phone_number()`

        .. note::
            If ``email_confirmation`` is ``True``, then user hasn't clicked the link yet.

        :return: see example below
        :rtype: :class:`dict`

        .. code:: python

            {'success': True,
             'email_confirmation': True,
             'error_text': '',
             'fatal': False}
        """
        sess = self._get_web_session()

        try:
            resp = sess.post('https://steamcommunity.com/steamguard/phoneajax',
                             data={
                                 'op': 'email_confirmation',
                                 'arg': '',
                                 'checkfortos': 1,
                                 'skipvoip': 1,
                                 'sessionid': sess.cookies.get('sessionid', domain='steamcommunity.com'),
                                 },
                             timeout=15).json()
        except:
            return {'fatal': True, 'success': False}

        return resp

    def confirm_phone_number(self, sms_code):
        """Confirm phone number with the recieved SMS code. See :meth:`add_phone_number()`

        :param sms_code: sms code
        :type  sms_code: :class:`str`
        :return: see example below
        :rtype: :class:`dict`

        .. code:: python

            {'success': True,
             'error_text': '',
             'fatal': False}
        """
        sess = self._get_web_session()

        try:
            resp = sess.post('https://steamcommunity.com/steamguard/phoneajax',
                             data={
                                 'op': 'check_sms_code',
                                 'arg': sms_code,
                                 'checkfortos': 1,
                                 'skipvoip': 1,
                                 'sessionid': sess.cookies.get('sessionid', domain='steamcommunity.com'),
                                 },
                             timeout=15).json()
        except:
            return {'success': False}

        return resp

    def has_phone_number(self):
        """Check whether the account has a verified phone number

        :return: see example below
        :rtype: :class:`dict`

        .. code:: python

            {'success': True,
             'has_phone': True,
             'error_text': '',
             'fatal': False}
        """
        sess = self._get_web_session()

        try:
            resp = sess.post('https://steamcommunity.com/steamguard/phoneajax',
                             data={
                                 'op': 'has_phone',
                                 'arg': '0',
                                 'checkfortos': 0,
                                 'skipvoip': 1,
                                 'sessionid': sess.cookies.get('sessionid', domain='steamcommunity.com'),
                                 },
                             timeout=15).json()
        except:
            return {'success': False}

        return resp

    def validate_phone_number(self, phone_number):
        """Test whether phone number is valid for Steam

        :param phone_number: phone number with country code
        :type  phone_number: :class:`str`
        :return: see example below
        :rtype: :class:`dict`

        .. code:: python

            {'is_fixed': False,
             'is_valid': False,
             'is_voip': True,
             'number': '+1 123-555-1111',
             'success': True}
        """
        sess = self._get_web_session()

        try:
            resp = sess.post('https://store.steampowered.com/phone/validate',
                             data={
                                'phoneNumber': phone_number,
                                'sessionID': sess.cookies.get('sessionid', domain='store.steampowered.com'),
                                },
                             allow_redirects=False,
                             timeout=15).json()
        except:
            resp = {'success': False}

        return resp


class SteamAuthenticatorError(Exception):
    pass


def generate_twofactor_code(shared_secret):
    """Generate Steam 2FA code for login with current time

    :param shared_secret: authenticator shared shared_secret
    :type shared_secret: bytes
    :return: steam two factor code
    :rtype: str
    """
    return generate_twofactor_code_for_time(shared_secret, time() + (get_time_offset() or 0))

def generate_twofactor_code_for_time(shared_secret, timestamp):
    """Generate Steam 2FA code for timestamp

    :param shared_secret: authenticator shared secret
    :type shared_secret: bytes
    :param timestamp: timestamp to use, if left out uses current time
    :type timestamp: int
    :return: steam two factor code
    :rtype: str
    """
    hmac = hmac_sha1(bytes(shared_secret),
                     struct.pack('>Q', int(timestamp)//30))  # this will NOT stop working in 2038

    start = ord(hmac[19:20]) & 0xF
    codeint = struct.unpack('>I', hmac[start:start+4])[0] & 0x7fffffff

    charset = '23456789BCDFGHJKMNPQRTVWXY'
    code = ''

    for _ in range(5):
        codeint, i = divmod(codeint, len(charset))
        code += charset[i]

    return code

def generate_confirmation_key(identity_secret, tag, timestamp):
    """Generate confirmation key for trades. Can only be used once.

    :param identity_secret: authenticator identity secret
    :type identity_secret: bytes
    :param tag: tag identifies what the request, see list below
    :type tag: str
    :param timestamp: timestamp to use for generating key
    :type timestamp: int
    :return: confirmation key
    :rtype: bytes

    Tag choices:

        * ``conf`` to load the confirmations page
        * ``details`` to load details about a trade
        * ``allow`` to confirm a trade
        * ``cancel`` to cancel a trade

    """
    data = struct.pack('>Q', int(timestamp)) + tag.encode('ascii') # this will NOT stop working in 2038
    return hmac_sha1(bytes(identity_secret), data)

def get_time_offset():
    """Get time offset from steam server time via WebAPI

    :return: time offset (``None`` when Steam WebAPI fails to respond)
    :rtype: :class:`int`, :class:`None`
    """
    try:
        resp = webapi.post('ITwoFactorService', 'QueryTime', 1, params={'http_timeout': 10})
    except:
        return None

    ts = int(time())
    return int(resp.get('response', {}).get('server_time', ts)) - ts

def generate_device_id(steamid):
    """Generate Android device id

    :param steamid: Steam ID
    :type steamid: :class:`.SteamID`, :class:`int`
    :return: android device id
    :rtype: str
    """
    h = hexlify(sha1_hash(str(steamid).encode('ascii'))).decode('ascii')
    return "android:%s-%s-%s-%s-%s" % (h[:8], h[8:12], h[12:16], h[16:20], h[20:32])

def extract_secrets_from_android_rooted(adb_path='adb'):
    """Extract Steam Authenticator secrets from a rooted Android device

    Prerequisite for this to work:

        - rooted android device
        - `adb binary <https://developer.android.com/studio/command-line/adb.html>`_
        - device in debug mode, connected and paired

    .. note::
        If you know how to make this work, without requiring the device to be rooted,
        please open a issue on github. Thanks

    :param adb_path: path to adb binary
    :type adb_path: str
    :raises: When there is any problem
    :return: all secrets from the device, steamid as key
    :rtype: dict
    """
    data = subprocess.check_output([
        adb_path, 'shell', 'su', '-c',
        "'cat /data/data/com.valvesoftware.android.steam.community/files/Steamguard*'"
        ])

    # When adb daemon is not running, `adb` will print a couple of lines before our data.
    # The data doesn't have new lines and its always on the last line.
    data = data.decode('utf-8').split('\n')[-1]

    if data[0] != "{":
        raise RuntimeError("Got invalid data: %s" % repr(data))

    return {int(x['steamid']): x
            for x in map(json.loads, data.replace("}{", '}|||||{').split('|||||'))}
