# -*- coding: utf-8 -*-
"""
This module simplifies the process of obtaining an authenticated session for steam websites.
After authentication is completed, a :class:`requests.Session` is created containing the auth cookies.
The session can be used to access ``steamcommunity.com``, ``store.steampowered.com``, and ``help.steampowered.com``.

.. warning::
    A web session may expire randomly, or when you login from different IP address.
    Some pages will return status code `401` when that happens.
    Keep in mind if you are trying to write robust code.

.. note::
    If you are using :class:`.SteamClient` take a look at :meth:`.SteamClient.get_web_session()`

.. note::
    If you need to authenticate as a mobile device for things like trading confirmations
    use :class:`MobileWebAuth` instead. The login process is identical, and in addition
    you will get :attr:`.oauth_token`.


Example usage:

.. code:: python

    import steam.webauth as wa

    user = wa.WebAuth('username')

    # At a console, cli_login can be used to easily perform all login steps
    session = user.cli_login('password')
    session.get('https://store.steampowered.com/account/history')

    # Or the login steps be implemented for other situation like so
    try:
        user.login('password')
    except (wa.CaptchaRequired, wa.LoginIncorrect) as exp:
        if isinstance(exp, LoginIncorrect):
            # ask for new password
        else:
            password = self.password

        if isinstance(exp, wa.CaptchaRequired):
            print user.captcha_url
            # ask a human to solve captcha
        else:
            captcha = None

        user.login(password=password, captcha=captcha)
    except wa.EmailCodeRequired:
        user.login(email_code='ZXC123')
    except wa.TwoFactorCodeRequired:
        user.login(twofactor_code='ZXC123')

    user.session.get('https://store.steampowered.com/account/history/')

"""
import json
from time import time, sleep
from base64 import b64encode
from getpass import getpass
import six
import requests

from steam.enums.proto import EAuthSessionGuardType
from steam.steamid import SteamID
from steam.utils.web import generate_session_id
from steam.core.crypto import rsa_publickey, pkcs1v15_encrypt


# TODO: Remove python2 support.
# TODO: Encrease min python version to 3.5

if six.PY2:
    intBase = long
    _cli_input = raw_input
else:
    intBase = int
    _cli_input = input

API_HEADERS = {
    'origin': 'https://steamcommunity.com',
    'referer': 'https://steamcommunity.com/',
    'accept': 'application/json, text/plain, */*'
}

API_URL = 'https://api.steampowered.com/{}Service/{}/v{}'

SUPPORTED_AUTH_TYPES = [EAuthSessionGuardType.EmailCode, EAuthSessionGuardType.DeviceCode, EAuthSessionGuardType.DeviceConfirmation]


class WebAuth(object):
    """New WEB Auth class.

    This class works with Steam API:
        https://steamapi.xpaw.me/#IAuthenticationService

    Currently, supports bsaic login/password auth with no 2FA, 2FA via
    steam guard code and 2FA via EMAIL confirmation.

    TODO: Add QR code support.

    TODO: Fully rework api handling. PUT api into separate class,
      in order to make this class responsible only for actual auth.

    IMPORTANT:
        Actually, at real login page
        steam handles function little bit different.
        e.g. https://api.steampowered.com/IAuthenticationService/BeginAuthSessionViaCredentials/v1
        can handle multipart/form-data; with something like.

        {
            input_protobuf_encoded: EgxhbmFjb25kYXJ0dXIa2AJodHgzZzlJaWY4dGE4RGxqR2VWbncwZWpxdi9uNDByRkZxaFduVk12VFFhRm1ZU1F4MHlrYUlJNmFURlVJWEQ5Z2VXMTlObWJDc3pydmNQZ1RTVllyOWl0SW5EWjgzMVh0YWtOaHJaUk9JN1lvMzhpb2xHRmdHdVBZT3NsekErTHZNZlJoQ3YzL1JFaEpNQlhjaXhzNklRRTZjbnM4d1JWbGI0TVA1Nzd0MHpGajRpcWF4U21KbnVjRDh5YzVIVkYvMERlMnFKd3dGTG0vR3B4SEdreFFlQURzZi9OTXJMTUszcWxnR3NLZm4ycGxNOGhkMzF3YnErSUlCZkNJb3dFZWExaUpJcmVjYkdLT0EvRlJ5VFpSQlVoVitLQmt6TGk3THY1UjVNYVRJSzNPTCtCMUZnZ2xWSG94c0ErTm5BMHVqSVZWZ0ZRdGpDL2tMTjd0SmhYamc9PSCA+aCT0ggoATgBQgVTdG9yZUqBAQp9TW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzExNi4wLjAuMCBTYWZhcmkvNTM3LjM2IE9QUi8xMDIuMC4wLjAQAlgI
        }
        it's protobuf encoded value. You can decode it here:
            https://protobuf-decoder.netlify.app

        some fields I can understand:
            2) string - steamlogin
            3) string - encrypted password
            4) timestamp to map to a key - STime
            5) some INT (probably it's always 1) it's DEPRECATED
            7) whether we are requesting a persistent or an ephemeral session
            8) (EMachineAuthWebDomain) identifier of client requesting auth.
               e.g. "Store"
            9) Protobuf of device type (see CAuthentication_DeviceDetails):
                9.1) string - User-Agent
                9.2) Int - platform identifier e.g. 2 (means Web Browser)
                    (See EAuthTokenPlatformType protobuf).
                9.3) os_type (MOSTLY NOT PRESENTED IN REAL REQUESTS)
                9.4) gaming_device_type (MOSTLY NOT PRESENTED IN REAL REQUESTS)
            11) UNDOCUMENTED AT ALL: Some number (like 8)

            FIELD NUMBERS I SKIPPED MEANS THEY ARE NOT PRESENTED IN REAL REQUEST
        We currently uses basic multipart/form-data and "key-value"
        data presentation.
        But I  Think, it's important to know, that real steam works differently,
        and maybe we can once upon a time simulate it's REAL behavior.

    """

    # Pretend to be chrome on windows, made this act as most like a
    # browser as possible to (hopefully) avoid breakage in the future from valve
    def __init__(self, username='', password='',
                 userAgent='Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
                           ' AppleWebKit/537.36 (KHTML, like Gecko)'
                           ' Chrome/118.0.0.0 Safari/537.36'):

        # ALL FUNCTIONS RENAMED TO PEP8 NOTATION.
        self.session = requests.session()
        self.user_agent = userAgent
        self.username = username
        self.password = password
        self.session.headers['User-Agent'] = self.user_agent
        self.steam_id = None
        self.client_id = None
        self.request_id = None
        self.refresh_token = None
        self.access_token = None
        self.session_id = None
        self.email_auth_waits = False  # Not used yet.
        self.logged_on = False

    @staticmethod
    def send_api_request(data, steam_api_interface, steam_api_method,
                         steam_api_version):
        """Send request to Steam API via requests"""
        steam_url = API_URL.format(steam_api_interface, steam_api_method,
                                   steam_api_version)

        if steam_api_method == "GetPasswordRSAPublicKey":  # It's GET method
            res = requests.get(steam_url, timeout=10, headers=API_HEADERS,
                               params=data)
        else:  # Every other API endpoints are POST.
            res = requests.post(steam_url, timeout=10, headers=API_HEADERS,
                                data=data)

        res.raise_for_status()
        return res.json()

    def _get_rsa_key(self):
        """Get rsa key to crypt password."""
        return self.send_api_request({'account_name': self.username},
                              "IAuthentication", 'GetPasswordRSAPublicKey', 1)

    def _encrypt_password(self):
        """Encrypt password via RSA key

        Steam handles every password only in encoded way.
        """
        r = self._get_rsa_key()

        mod = intBase(r['response']['publickey_mod'], 16)
        exp = intBase(r['response']['publickey_exp'], 16)

        pub_key = rsa_publickey(mod, exp)
        encrypted = pkcs1v15_encrypt(pub_key, self.password.encode('ascii'))
        b64 = b64encode(encrypted)

        return tuple((b64.decode('ascii'), r['response']['timestamp']))

    def _startSessionWithCredentials(self, account_encrypted_password: str,
                                     time_stamp: int):
        """Start login session via BeginAuthSessionViaCredentials


        """
        resp = self.send_api_request(
            {'device_friendly_name': self.user_agent,
             'account_name': self.username,
             'encrypted_password': account_encrypted_password,
             'encryption_timestamp': time_stamp,
             'remember_login': '1',
             'platform_type': '2',
             'persistence': '1',
             'website_id': 'Community',
             },
            'IAuthentication',
            'BeginAuthSessionViaCredentials',
            1
        )
        self.client_id = resp['response']['client_id']
        self.request_id = resp['response']['request_id']
        self.steam_id = SteamID(resp['response']['steamid'])
        self.allowed_confirmations = [EAuthSessionGuardType(confirm_type['confirmation_type']) for confirm_type in resp['response']['allowed_confirmations']]

    def _startLoginSession(self):
        """Starts login session via credentials."""
        encrypted_password = self._encrypt_password()
        self._startSessionWithCredentials(encrypted_password[0],
                                          encrypted_password[1])

    def _pollLoginStatus(self):
        """Get status of current Login Session

        This function asks server about login session status.
        If we logged in, this returns access_token that we needed.

        TODO: add check of interval, returned from _startSessionWithCredentials
            actually it has no need now, but
        """
        resp = self.send_api_request({
            'client_id': str(self.client_id),
            'request_id': str(self.request_id)
        }, 'IAuthentication', 'PollAuthSessionStatus', 1)
        try:
            self.refresh_token = resp['response']['refresh_token']
            self.access_token = resp['response']['access_token']
        except KeyError:
            raise TwoFactorAuthNotProvided('Authentication requires 2fa token, which is not provided or invalid')

    def _finalizeLogin(self):
        self.sessionID = generate_session_id()
        self.logged_on = True
        for domain in ['store.steampowered.com', 'help.steampowered.com',
                       'steamcommunity.com']:
            self.session.cookies.set('sessionid', self.sessionID, domain=domain)
            self.session.cookies.set('steamLoginSecure',
                                     str(self.steam_id.as_64) + "||" + str(
                                         self.access_token), domain=domain)

    def _update_login_token(
            self,
            code: str,
            code_type: EAuthSessionGuardType = EAuthSessionGuardType.DeviceCode
    ):
        """Send 2FA token to steam

        Please note, that very rare, login can be unsuccessful,
        if you use code, that guard provided you BEFORE log in session
        was started. To fix it, just rerun login.

        """
        data = {
            'client_id': self.client_id,
            'steamid': self.steam_id,
            'code': code,
            'code_type': code_type
        }
        res = self.send_api_request(data, 'IAuthentication',
                             'UpdateAuthSessionWithSteamGuardCode', 1)
        return res


    def login(self, username: str = '', password: str = '', code: str = None,
              email_required=False):
        """Log in user by new Steam API

        If user has no need 2FA, this function will just  log in user.
        If 2FA SteamGuard code needed, when user can provide it just
        with guard.SteamAuthenticator.get_code like it always was.

        If Email code is required, when user can provide email_required.
        If email_required was provided, when this function only setup auth
        and return new function.

        this function will receive email code. Once email code will be provided
        authentication process will be complete.
        If wrong code provided in this new function, when error will be raised.
        And new code will be waited.

        """
        if self.logged_on:
            return self.session

        username = username or self.username
        password = password or self.password

        if username == '' or password == '':
            raise LoginIncorrect("Username or password is provided empty!")
        else:
            self.username = username
            self.password = password

        self._startLoginSession()
        if code:
            self._update_login_token(code)
        if email_required:
            # We do another request, which force steam to send email code
            # (otherwise code just not sent).

            url = (f'https://login.steampowered.com/jwt/checkdevice/'
                   f'{self.steam_id}')
            res = self.session.post(url, data={
                'clientid': self.client_id,
                'steamid': self.steam_id
            }).json()
            if res.get('result') == 8:
                # This usually mean code sent now.
                def end_login(email_code: str):
                    self._update_login_token(email_code,
                                             EAuthSessionGuardType.EmailCode)
                    self._pollLoginStatus()
                    self._finalizeLogin()
                    return self.session
                return end_login
            if res.get('result') == 29:
                # This code 100% means some data not valid
                # Actually this must will never be called, because
                # Errors can be only like wrong cookies. (Theoretically)
                raise WebAuthException("Something invalid went. Try again later.")
        self._pollLoginStatus()
        self._finalizeLogin()

        return self.session

    def logout_everywhere(self):
        """Log out on every device.

        This function works just like button at
        https://store.steampowered.com/twofactor/manage
        and allows user to logout on every device.
        Can be VERY useful e.g. for users, who practice account rent.
        """
        session_id = self.session.cookies.get('sessionid',
                    domain='store.steampowered.com')

        # By the times I saw session can be both of keys, so select valid.
        session_id = session_id or self.session.cookies.get(
                'sessionId', domain='store.steampowered.com')
        data = {
            "action": "deauthorize",
            "sessionid": session_id
        }
        resp = self.session.post(
            'https://store.steampowered.com/twofactor/manage_action',
            data=data
        )

        return resp.status_code == 200

    def cli_login(self, username: str = '', password: str = '', code: str =     '',
                      email_required: bool = False):
        """Generates CLI prompts to perform the entire login process

        If you use email confirm, provide email_required = True,
        else just provide code.
        """
        while True:
            try:
                res = self.login(
                    username,
                    password,
                    code,
                    email_required
                )
            except LoginIncorrect:
                prompt = ("Enter password for %s: " if not password else "Invalid password for %s. Enter password:")
                password = getpass(prompt % repr(self.username))
                continue
            except TwoFactorAuthNotProvided:
                # 2FA handling
                allowed = set(self.allowed_confirmations)
                if allowed.isdisjoint(SUPPORTED_AUTH_TYPES):
                    raise AuthTypeNotSupported("Couldn't find a supported auth type for this account.")

                can_confirm_with_app = EAuthSessionGuardType.DeviceConfirmation in allowed

                twofactor_code = ''
                while twofactor_code.strip() == '':
                    prompt = ''
                    if EAuthSessionGuardType.DeviceCode in allowed:
                        prompt = 'Enter your Steam Guard code'
                    elif EAuthSessionGuardType.EmailCode in allowed:
                        prompt = 'Enter the Steam 2FA code emailed to you'
                    if can_confirm_with_app:
                        if prompt == '':
                            # don't think this is possible, but let's handle it anyways
                            input("Please confirm Steam Guard on your device and press ENTER to continue")
                        else:
                            prompt += ' (or simply press Enter if approved via app)'

                    if prompt != '':
                        prompt += ': '
                        twofactor_code = input(prompt) 

                    if can_confirm_with_app:
                        try:
                            self._pollLoginStatus() # test to see if they've authenticated via app
                            break
                        except TwoFactorAuthNotProvided:
                            # they've not authenticated via the app, let's see if we can use their provided code
                            pass

                    if twofactor_code.strip():
                        using_email_code = EAuthSessionGuardType.EmailCode in allowed
                        self._update_login_token(twofactor_code, EAuthSessionGuardType.EmailCode if using_email_code else EAuthSessionGuardType.DeviceCode)
                        try:
                            self._pollLoginStatus()
                            break
                        except TwoFactorAuthNotProvided:
                            print("Invalid auth code. Please try again")
                            twofactor_code = ''
                            continue
                    else:
                        print("Unauthenticated. Please try again")
                self._finalizeLogin()
                return self.session
            if hasattr(res, '__call__'):
                # this should not ever happen at this point as we don't use `email_required` on login()
                while True:
                    try:
                        twofactor_code = input('Enter your 2fa/email code: ')
                        resp = res(twofactor_code)
                        return resp
                    except WebAuthException:
                        pass
            else:
                return self.session


#TODO: DEPRECATED, must be rewritten, like WebAuth
class MobileWebAuth(WebAuth):
    """Identical to :class:`WebAuth`, except it authenticates as a mobile device."""
    oauth_token = None  #: holds oauth_token after successful login

    def _send_login(self, password='', captcha='', email_code='',
                    twofactor_code=''):
        data = {
            'username': self.username,
            "password": b64encode(
                pkcs1v15_encrypt(self.key, password.encode('ascii'))),
            "emailauth": email_code,
            "emailsteamid": str(self.steam_id) if email_code else '',
            "twofactorcode": twofactor_code,
            "captchagid": self.captcha_gid,
            "captcha_text": captcha,
            "loginfriendlyname": "python-steam webauth",
            "rsatimestamp": self.timestamp,
            "remember_login": 'true',
            "donotcache": int(time() * 100000),
            "oauth_client_id": "DE45CD61",
            "oauth_scope": "read_profile write_profile read_client write_client",
        }

        self.session.cookies.set('mobileClientVersion', '0 (2.1.3)')
        self.session.cookies.set('mobileClient', 'android')

        try:
            return self.session.post(
                'https://steamcommunity.com/login/dologin/', data=data,
                timeout=15).json()
        except requests.exceptions.RequestException as e:
            raise HTTPError(str(e))
        finally:
            self.session.cookies.pop('mobileClientVersion', None)
            self.session.cookies.pop('mobileClient', None)

    def _finalize_login(self, login_response):
        data = json.loads(login_response['oauth'])
        self.steam_id = SteamID(data['steamid'])
        self.oauth_token = data['oauth_token']

    def oauth_login(self, oauth_token='', steam_id='', language='english'):
        """Attempts a mobile authenticator login using an oauth token, which can be obtained from a previously logged-in
        `MobileWebAuth`

        :param oauth_token: oauth token string, if it wasn't provided on instance init
        :type  oauth_token: :class:`str`
        :param steam_id: `SteamID` of the account to log into, if it wasn't provided on instance init
        :type  steam_id: :class:`str` or :class:`SteamID`
        :param language: select language for steam web pages (sets language cookie)
        :type  language: :class:`str`
        :return: a session on success and :class:`None` otherwise
        :rtype: :class:`requests.Session`, :class:`None`
        :raises HTTPError: any problem with http request, timeouts, 5xx, 4xx etc
        :raises LoginIncorrect: Invalid token or SteamID
        """
        if oauth_token:
            self.oauth_token = oauth_token
        elif self.oauth_token:
            oauth_token = self.oauth_token
        else:
            raise LoginIncorrect('token is not specified')

        if steam_id:
            self.steam_id = SteamID(steam_id)
        elif not self.steam_id:
            raise LoginIncorrect('steam_id is not specified')

        steam_id = self.steam_id.as_64

        data = {
            'access_token': oauth_token
        }

        try:
            resp = self.session.post(
                'https://api.steampowered.com/IMobileAuthService/GetWGToken/v0001',
                data=data)
        except requests.exceptions.RequestException as e:
            raise HTTPError(str(e))

        try:
            resp_data = resp.json()['response']
        except json.decoder.JSONDecodeError as e:
            if 'Please verify your <pre>key=</pre> parameter.' in resp.text:
                raise LoginIncorrect('invalid token')
            else:
                raise e

        self.session_id = generate_session_id()

        for domain in ['store.steampowered.com', 'help.steampowered.com',
                       'steamcommunity.com']:
            self.session.cookies.set('birthtime', '-3333', domain=domain)
            self.session.cookies.set('sessionid', self.session_id,
                                     domain=domain)
            self.session.cookies.set('mobileClientVersion', '0 (2.1.3)',
                                     domain=domain)
            self.session.cookies.set('mobileClient', 'android', domain=domain)
            self.session.cookies.set('steamLogin',
                                     str(steam_id) + "%7C%7C" + resp_data[
                                         'token'], domain=domain)
            self.session.cookies.set('steamLoginSecure',
                                     str(steam_id) + "%7C%7C" + resp_data[
                                         'token_secure'],
                                     domain=domain, secure=True)
            self.session.cookies.set('Steam_Language', language, domain=domain)

        self.logged_on = True

        return self.session


class WebAuthException(Exception):
    pass


class AuthTypeNotSupported(WebAuthException):
    pass


class TwoFactorAuthNotProvided(WebAuthException):
    pass


class HTTPError(WebAuthException):
    pass


class LoginIncorrect(WebAuthException):
    pass


class CaptchaRequired(WebAuthException):
    pass


class CaptchaRequiredLoginIncorrect(CaptchaRequired, LoginIncorrect):
    pass


class EmailCodeRequired(WebAuthException):
    pass


class TwoFactorCodeRequired(WebAuthException):
    pass


class TooManyLoginFailures(WebAuthException):
    pass
