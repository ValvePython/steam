"""
This submodule contains various functionality related to Steam Guard.

:class:`SteamAuthenticator` provides methods for genereating codes
and enabling 2FA on a Steam account. Operations managing the authenticator
on an account require an instance of either :class:`.MobileWebAuth` or 
:class:`.SteamClient`. The instance needs to be logged in.

Adding an authenticator

.. code:: python

    sa = SteamAuthenticator(medium=medium)
    sa.add()  # SMS code will be send to account's phone number
    sa.finalize('SMS CODE')

    sa.secrets  # dict with authenticator secrets

    sa.get_code()  # 2FA code for login

    sa.remove()  # removes the authenticator from the account

.. warning::
    Once the authenticator is enabled, make sure you save your secrets.
    Otherwise you will lose access to the account.

Once authenticator is enabled all you need is the secrets to generate codes.

.. code:: python

    sa = SteamAuthenticator(secrets)
    sa.get_code()

"""
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
from steam.util import proto_to_dict


class SteamAuthenticator(object):
    """Add/Remove authenticator from an account. Generate 2FA and confirmation codes."""
    _finalize_attempts = 5
    medium =  None            #: instance of :class:`.MobileWebAuth` or :class:`.SteamClient`
    steam_time_offset = None  #: offset from steam server time
    secrets = None            #: :class:`dict` with authenticator secrets

    def __init__(self, secrets=None, medium=None):
        """
        :param secret: a dict of authenticator secrets
        :type secret: dict
        :param medium: logged on session for steam user
        :type mediumm: :class:`.MobileWebAuth`, :class:`.SteamClient`
        """
        self.secrets = secrets or {}
        self.medium = medium

    def __getattr__(self, key):
        if key not in self.secrets:
            raise AttributeError("No such attribute")
        return self.secrets[key]

    def get_time(self):
        """
        :return: Steam aligned timestamp
        :rtype: int
        """
        if self.steam_time_offset is None:
            self.steam_time_offset = get_time_offset()
        return int(time() + self.steam_time_offset)

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
        :param tag: see :func:`generate_confimation_key` for this value
        :type tag: str
        :param timestamp: time to use for code generation
        :type timestamp: int
        :return: trade confirmation key
        :rtype: str
        """
        return generate_confirmation_key(b64decode(self.identity_secret), tag,
                                         self.get_time() if timestamp is None else timestamp)

    def _send_request(self, action, params):
        action_map = {
            'add':          'AddAuthenticator',
            'finalize':     'FinalizeAddAuthenticator',
            'remove':       'RemoveAuthenticator',
            'status':       'QueryStatus',
            'createcodes':  'CreateEmergencyCodes',
            'destroycodes': 'DestroyEmergencyCodes',
        }
        medium = self.medium

        if isinstance(medium, MobileWebAuth):
            if not medium.complete:
                raise SteamAuthenticatorError("MobileWebAuth instance not logged in")

            params['access_token'] = medium.oauth_token
            params['http_timeout'] = 10

            try:
                resp = webapi.post('ITwoFactorService', action_map[action], 1, params=params)
            except requests.exceptions.RequestException as exp:
                raise SteamAuthenticatorError("Error adding via WebAPI: %s" % str(exp))

            resp = resp['response']
        else:
            if not medium.logged_on:
                raise SteamAuthenticatorError("SteamClient instance not logged in")

            resp = medium.unified_messages.send_and_wait("TwoFactor.%s#1" % action_map[action],
                                                         params, timeout=10)
            if resp is None:
                raise SteamAuthenticatorError("Failed to add authenticator. Request timeout")

            resp = proto_to_dict(resp)

            if action == 'add':
                for key in ['shared_secret', 'identity_secret', 'secret_1']:
                    resp[key] = b64encode(resp[key])

        return resp

    def add(self):
        """Add authenticator to an account.
        The account's phone number will receive a SMS code required for :meth:`finalize`.

        :raises: :class:`SteamAuthenticatorError`
        """
        params = {
            'steamid': self.medium.steam_id,
            'authenticator_time': int(time()),
            'authenticator_type': int(ETwoFactorTokenType.ValveMobileApp),
            'device_identifier': generate_device_id(self.medium.steam_id),
            'sms_phone_id': '1',
        }

        resp = self._send_request('add', params)

        if resp['status'] != EResult.OK:
            raise SteamAuthenticatorError("Failed to add authenticator. Error: %s" % repr(EResult(resp['status'])))

        for key in ['shared_secret', 'identity_secret', 'serial_number', 'secret_1', 'revocation_code', 'token_gid']:
            if key in resp:
                self.secrets[key] = resp[key]

        self.steam_time_offset = int(resp['server_time']) - time()

    def finalize(self, activation_code):
        """Finalize authenticator with received SMS code

        :param activation_code: SMS code
        :type activation_code: str
        :raises: :class:`SteamAuthenticatorError`
        """
        params = {
            'steamid': self.medium.steam_id,
            'authenticator_time': int(time()),
            'authenticator_code': self.get_code(),
            'activation_code': activation_code,
        }

        resp = self._send_request('finalize', params)

        if resp['status'] != EResult.TwoFactorActivationCodeMismatch and resp.get('want_more', False) and self._finalize_attempts:
            self.steam_time_offset += 30
            self._finalize_attempts -= 1
            self.finalize(activation_code)
            return
        elif not resp['success']:
            self._finalize_attempts = 5
            raise SteamAuthenticatorError("Failed to finalize authenticator. Error: %s" % repr(EResult(resp['status'])))

        self.steam_time_offset = int(resp['server_time']) - time()

    def remove(self):
        """Remove authenticator

        .. warning::
            Doesn't work via :class:`.SteamClient`. Disabled by Valve

        :raises: :class:`SteamAuthenticatorError`
        """
        if not self.secrets:
            raise SteamAuthenticatorError("No authenticator secrets available?")

        params = {
            'steamid': self.medium.steam_id,
            'revocation_code': self.revocation_code,
            'steamguard_scheme': 1,
        }

        resp = self._send_request('remove', params)

        if not resp['success']:
            raise SteamAuthenticatorError("Failed to remove authenticator. (attempts remaining: %s)" % (
                resp['revocation_attempts_remaining'],
                ))

        self.secrets.clear()

    def status(self, medium=None):
        """Fetch authenticator status for the account

        :raises: :class:`SteamAuthenticatorError`
        :return: dict with status parameters
        :rtype: dict
        """
        params = {'steamid': self.medium.steam_id}
        return self._send_request('status', params)

    def create_emergency_codes(self):
        """Generate emergency codes

        :raises: :class:`SteamAuthenticatorError`
        :return: list of codes
        :rtype: list
        """
        return self._send_request('createcodes', {}).get('code', [])

    def destroy_emergency_codes(self):
        """Destroy all emergency codes

        :raises: :class:`SteamAuthenticatorError`
        """
        params = {'steamid': self.medium.steam_id}
        self._send_request('destroycodes', params)


class SteamAuthenticatorError(Exception):
    pass


def generate_twofactor_code(shared_secret):
    """Generate Steam 2FA code for login with current time

    :param shared_secret: authenticator shared shared_secret
    :type shared_secret: bytes
    :return: steam two factor code
    :rtype: str
    """
    return generate_twofactor_code_for_time(shared_secret, time() + get_time_offset())

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

def generate_confirmation_key(identity_secret, timestamp, tag=''):
    """Generate confirmation key for trades. Can only be used once.

    :param identity_secret: authenticator identity secret
    :type identity_secret: bytes
    :param timestamp: timestamp to use for generating key
    :type timestamp: int
    :param tag: tag identifies what the request, see list below
    :type tag: str
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

    :return: time offset
    :rtype: int
    """
    try:
        resp = webapi.post('ITwoFactorService', 'QueryTime', 1, params={'http_timeout': 10})
    except:
        return 0

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
