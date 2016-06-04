"""
This module is used to safely store account credentials and provide mobile authenticator codes.

Example usage:

.. code:: python

    import steam.account

    account = steam.account.SteamAccount('username', 'password')
    account.set_account_property('identity_secret', 'XYZ')
    account.set_account_property('shared_secret', 'XYZ')
    code    = account.login_code
    key     = account.get_confirmation_key('conf')



TODO:
    - Where to save the credentials (Windows/Linux)?
    - Implement mobile authenticator features?
"""
import os
import sys
import json
import base64

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

from steam.guard import *

if sys.platform.startswith('win'):
    BASE_LOCATION = '.' #Windows
else:
    BASE_LOCATION = '.'

ACCOUNT_ATTRIBUTES = ['username', 'password', 'steamid', 'shared_secret', 'identity_secret']

class SteamAccount(object):
    username            = None
    password            = None
    _path               = None
    _file               = None
    _fernet_key         = None
    _fernet_suite       = None

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self._setup()

    def __del__(self):
        try:
            self._update_credential_file()
        except TypeError:
            """
            Ignore TypeError exception when destructor gets called after the memory has been cleared
            """
            pass
        self._file.close()

    def set_account_property(self, property, value):
        setattr(self, property, value)
        self._update_credential_file()

    @property
    def login_code(self):
        try:
            return generate_twofactor_code(self.shared_secret)
        except AttributeError:
            raise SharedSecretNotSet('Add shared_secret to this instance to generate login codes')

    def get_confirmation_key(self, tag, timestamp=None):
        if not timestamp:
            timestamp = get_time_offset()
        try:
            return generate_confirmation_key(self.identity_secret, timestamp, tag)
        except AttributeError:
            raise IdentitySecretNotSet('Add identity_secret to this instance to generate confirmation keys')

    def _setup(self):
        self._generate_fernet_key()
        self._spawn_fernet_suite()
        self._path = '%s/%s' % (BASE_LOCATION, self.username)
        self._file = open(self._path, 'r+')
        if not os.path.isfile(self._path):
            self._create_credential_file()
        else:
            credentials = self._parse_credential_file()
            for key, value in credentials.iteritems():
                setattr(self, key, value)

    def _create_credential_file(self):
        data = json.dumps({
            'username': self.username,
            'password': self.password
        })
        text = self._fernet_suite.encrypt(data)
        self._file.write(text)

    def _parse_credential_file(self):

        text = self._file.read()
        data = json.loads(self._fernet_suite.decrypt(text))
        return data

    def _update_credential_file(self):
        credentials = self._gather_credentials()
        data = json.dumps(credentials)

        text = self._fernet_suite.encrypt(data)
        self._file.truncate()
        self._file.write(text)

    def _gather_credentials(self):
        data = { }
        names = dir(self)
        for name in names:
            if name in ACCOUNT_ATTRIBUTES:
                data.__setitem__(name, getattr(self, name))
        return data

    def _generate_fernet_key(self):
        digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
        digest.update(bytes(self.password))
        self._fernet_key = base64.urlsafe_b64encode(digest.finalize())

    def _spawn_fernet_suite(self):
        self._fernet_suite = Fernet(self._fernet_key)

class SteamAccountException(Exception):
    pass

class SharedSecretNotSet(SteamAccountException):
    pass

class IdentitySecretNotSet(SteamAccountException):
    pass