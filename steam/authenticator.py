"""
This module provides methods for managing the mobile authenticator

.. warning::
    Save your credentials!

Example usage:

.. code:: python

    import steam.authenticator

    ma = steam.authenticator.MobileAuthenticator('username', 'password')
    credentials = ma.add_authenticator()

    sms_code = raw_input('SMS Code: ')

    ma.finalize_authenticator(sms_code)

    print credentials

"""
import json

from guard import *
from mobile import SteamMobile


class MobileAuthenticator(object):
    mobile = None

    def __init__(self, username, password, login_mode='normal', email_code='', twofactor_code=''):
        self.mobile = SteamMobile(username, password, login_mode, email_code, twofactor_code)

    def add_authenticator(self):
        """Start process of linking a mobile authenticator to the logged in steam account

        :return: account credentials or False
        :rtype: :class:`tuple`, :class:`bool`
        """

        data = {
            'steamid': self.mobile.steamid,
            'sms_phone_id': 1,
            'access_token': self.mobile.oauth['oauth_token'],
            'authenticator_time': get_time_offset(),
            'authenticator_type': 1,
            'device_identifier': generate_device_id(self.mobile.steamid)
        }

        [status, body] = self.mobile.api_request('ITwoFactorService', 'AddAuthenticator', data,
                                                 return_including_status_code=True)
        if status == 200:
            responseData = json.loads(body)
            self.credentials = responseData['response']
            self.credentials['secret'] = self.credentials['uri'].split('?secret=')[1].split('&issuer')[0]
            return responseData
        else:
            return False

    def finalize_authenticator(self, sms_code=None, tries=1):
        """Start process of linking a mobile authenticator to the logged in steam account

        :param sms_code: text reponse recieved by sms
        :type sms_code: :class:`str`
        :return: :class:`None` it no sms code is supplied, `True` or `False`
        :rtype: :class:`None`, :class:`bool`
        """

        if not sms_code:
            return None

        timestamp = get_time_offset()

        data = {
            'steamid': self.mobile.steamid,
            'access_token': self.mobile.oauth['oauth_token'],
            'authenticator_time': timestamp,
            'authenticator_code': generate_twofactor_code_for_time(self.credentials['shared_secret'], timestamp),
            'activation_code': sms_code
        }
        [status, body] = self.mobile.api_request('ITwoFactorService', 'FinalizeAddAuthenticator', data,
                                                 return_including_status_code=True)
        if status == 200:
            responseData = json.loads(body)['response']
            if responseData['success']:
                return True
            else:
                if responseData['want_more'] and tries < 30:
                    return self.finalizeAuthenticator(sms_code, tries)
                else:
                    return False
        else:
            return False


class MobileAuthenticatorException(Exception):
    pass