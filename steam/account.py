"""
This module is used to safely store account credentials and provide mobile authenticator codes.

Example usage:

.. code:: python

    import steam.account

    account = steam.account.SteamAccount('username', 'password')
    account.set_account_property('identity_secret', 'XYZ')
    account.set_account_property('shared_secret', 'XYZ')
    api_key    = account.get_api_key()
"""
import os
import sys
import json
import base64
import re
import atexit
from base64 import b64decode

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

import steam.guard
import steam.webauth
import steam.webapi

if sys.platform.startswith('win'):
    BASE_LOCATION = '.' #Windows
else:
    BASE_LOCATION = '.'

ACCOUNT_ATTRIBUTES = ['username', 'password', 'steamid', 'shared_secret', 'identity_secret', 'revocation_code',\
                      'secret_1', 'serial_number', 'deviceid', 'oauth_token', 'apikey']

class SteamAccount(object):
    username            = None
    password            = None

    mobile_session      = None
    web_session         = None
    web_api             = None
    authenticator       = None

    _credentials        = { }
    _path               = None
    _file               = None
    _fernet_key         = None
    _fernet_suite       = None
    _web_auth           = None
    _mobile_auth        = None


    def __init__(self, username, password):
        atexit.register(self.__cleanup__)
        self.username = username
        self.password = password
        if not self._setup():
            raise SteamAccountException('Could not access account.')

    def __getattr__(self, key):
        if key not in self._credentials.keys():
            raise AttributeError("No %s attribute" % repr(key))
        return self._credentials.get(key)

    def __del__(self):
        self.__save_account_credentials__()

    def __cleanup__(self):
        self.__save_account_credentials__()

    def __save_account_credentials__(self):
        """
        Make sure it doesnt write the file if the memory has been cleared
        """
        if self._count_account_credentials() <= 2:
            return
        try:
            self._update_credential_file()
        except TypeError:
            """
            Ignore TypeError exception when destructor gets called after the memory has been cleared
            """
            pass
        except ValueError:
            """
            Ignore ValueError exception when the file could not be written
            """
            pass

    def set_account_property(self, property, value):
        self._credentials[property] = value
        self._update_credential_file()

    def del_account_property(self, property):
        del self._credentials[property]
        self._update_credential_file()

    def check_account_property(self, property):
        return property in self._credentials

    @property
    def login_code(self):
        if self.authenticator and hasattr(self.authenticator, 'shared_secret'):
            return self.authenticator.get_code()
        elif hasattr(self, 'shared_secret'):
            return steam.guard.generate_twofactor_code(b64decode(self.shared_secret))
        else:
            raise SharedSecretNotSet('Add shared_secret to this instance to generate login codes')

    def get_api_key(self, retrieve_if_missing=False, hostname_for_retrieving='localhost.com'):
        if self.check_account_property('apikey'):
            return self.apikey

        elif retrieve_if_missing:
            if not self._has_web_session():
                self._spawn_web_session()

            api_key = self.retrieve_api_key(hostname_for_retrieving)
            self.set_account_property('apikey', api_key)
            self._spawn_web_api()
            return api_key
        else:
            raise APIKeyException('Could not return the apikey. The apikey is not set as account property and retrieve_if_missing is not allowed.')

    def retrieve_api_key(self, hostname_for_retrieving='localhost.com'):
        if not self._has_web_session():
            raise APIKeyException('A web session is required to retrieve the api key.')

        response = self.web_session.get('https://steamcommunity.com/dev/apikey')

        if 'Access Denied' in response.text:
            raise APIKeyException('You need at least 1 game on this account to access the steam api key page.')

        else:
            if 'Register for a new Steam Web API Key' in response.text:
                regex_result = re.search(r'<input type="hidden" name="sessionid" value="(.*)">', response.text)
                session_id = regex_result.group(1)

                data = {
                    'domain': hostname_for_retrieving,
                    'agreeToTerms': 'agreed',
                    'submit': 'Register',
                    'sessionid': session_id
                }

                self.web_session.post('https://steamcommunity.com/dev/registerkey', data=data)
                return self.retrieve_api_key()

            elif 'Your Steam Web API Key' in response.text:
                regex_result = re.search(r'<p>Key: (.*)</p>', response.text)
                api_key = regex_result.group(1)
                return api_key

            else:
                raise APIKeyException('An unhandled api key page appeared, please try again.')

    def _setup(self):
        self._generate_fernet_key()
        self._spawn_fernet_suite()
        self._path = '%s/%s' % (BASE_LOCATION, self.username)
        if not os.path.exists(self._path) or not os.path.isfile(self._path):
            self._create_credential_file()
        else:
            credentials = self._parse_credential_file()
            for key, value in credentials.iteritems():
                self._credentials[key] = value

            if self.check_account_property('shared_secret'):
                self._spawn_authenticator()

            else:
                self.authenticator = steam.guard.SteamAuthenticator()

            if self.check_account_property('apikey'):
                self._spawn_web_api()
        return True

    def _create_credential_file(self):
        open(self._path, 'w+').close()
        self._spawn_file_pointer()

        data = json.dumps({
            'username': self.username,
            'password': self.password
        })

        token = self._fernet_suite.encrypt(data)
        self._file.write(token)
        self._file.close()

    def _parse_credential_file(self):
        self._spawn_file_pointer()

        token = self._file.read()
        data = json.loads(self._fernet_suite.decrypt(token))
        self._file.close()
        return data

    def _update_credential_file(self):
        self._spawn_file_pointer()

        credentials = self._gather_credentials()
        data = json.dumps(credentials)
        token = self._fernet_suite.encrypt(data)

        self._file.truncate()
        self._file.write(token)
        self._file.close()

    def _gather_credentials(self):
        data = { }
        names = self._credentials
        for name in names:
            if name in ACCOUNT_ATTRIBUTES:
                data.__setitem__(name, self._credentials[name])
        return data

    def _count_account_credentials(self):
        count = 0
        for attr in ACCOUNT_ATTRIBUTES:
            if self.check_account_property(attr):
                count += 1
        return count

    def _generate_fernet_key(self):
        digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
        digest.update(bytes(self.password))
        self._fernet_key = base64.urlsafe_b64encode(digest.finalize())

    def _spawn_fernet_suite(self):
        self._fernet_suite = Fernet(self._fernet_key)

    def _spawn_file_pointer(self):
        self._file = open(self._path, 'r+', 0)

    def _spawn_web_api(self):
        self.web_api = steam.webapi.WebAPI(self.apikey)

    def _spawn_authenticator(self):
        secrets = {
            'identity_secret':  self._credentials.get('identity_secret'),
            'shared_secret':    self._credentials.get('shared_secret'),
            'secret_1':         self._credentials.get('secret_1'),
            'revocation_code':  self._credentials.get('revocation_code'),
            'deviceid':         self._credentials.get('deviceid')
        }
        self.authenticator = steam.guard.SteamAuthenticator(secrets)
        self._spawn_mobile_session()
        self.authenticator.medium = self._mobile_auth

    def _has_session(self):
        return True if self._has_web_session() or self._has_mobile_session() else False

    def _has_web_session(self):
        return isinstance(self._web_auth, steam.webauth.WebAuth)

    def _has_mobile_session(self):
        return isinstance(self._mobile_auth, steam.webauth.MobileWebAuth)

    def _spawn_web_session(self):
        self._web_auth = steam.webauth.WebAuth(self.username, self.password)
        self._login_web_session(self._web_auth)
        self.web_session = self._web_auth.session

    def _spawn_mobile_session(self):
        self._mobile_auth = steam.webauth.MobileWebAuth(self.username, self.password)
        self._login_web_session(self._mobile_auth)
        self.mobile_session = self._mobile_auth.session

    def _login_web_session(self, web_auth):
        if not isinstance(web_auth, steam.webauth.WebAuth) and not isinstance(web_auth, steam.webauth.MobileWebAuth):
            raise WebAuthNotComplete('Please supply a valid WebAuth or MobileWebAuth session')

        try:
            twofactor_code = self.login_code
        except SharedSecretNotSet:
            twofactor_code = ''

        web_auth.login(twofactor_code=twofactor_code)

        if web_auth.complete:
            if not hasattr(self, 'steamid'):
                self.set_account_property('steamid', web_auth.steam_id)

            if isinstance(web_auth, steam.webauth.MobileWebAuth):
                self.set_account_property('oauth_token', web_auth.oauth_token)
        else:
            raise WebAuthNotComplete('The web authentication could not be completed.')

class SteamAccountException(Exception):
    pass

class SharedSecretNotSet(SteamAccountException):
    pass

class IdentitySecretNotSet(SteamAccountException):
    pass

class WebAuthNotComplete(SteamAccountException):
    pass

class WebException(SteamAccountException):
    pass

class APIKeyException(SteamAccountException):
    pass

class ParameterNotProvidedException(SteamAccountException):
    pass