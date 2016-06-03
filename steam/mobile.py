# -*- coding: utf-8 -*-
"""
This module provides utility functions to access steam mobile pages
"""

import json
import requests

import mobileauth

API_ENDPOINTS = {
    "IMobileAuthService": {
        "methods": {
            "GetWGToken": {
                "version": 1
            }
        }
    },
    "ISteamWebUserPresenceOAuth": {
        "methods": {
            "Logon": {
                "version": 1
            },
            "Logoff": {
                "version": 1
            },
            "Message": {
                "version": 1
            },
            "DeviceInfo": {
                "version": 1
            },
            "Poll": {
                "version": 1
            }
        }
    },
    "ISteamUserOAuth": {
        "methods": {
            "GetUserSummaries": {
                "version": 1
            },
            "GetGroupSummaries": {
                "version": 1
            },
            "GetGroupList": {
                "version": 1
            },
            "GetFriendList": {
                "version": 1
            },
            "Search": {
                "version": 1
            }
        }
    },

    "ISteamGameOAuth": {
        "methods": {
            "GetAppInfo": {
                "version": 1
            }
        }
    },
    "IMobileNotificationService": {
        "methods": {
            "SwitchSessionToPush": {
                "version": 1
            }
        }
    },
    "IFriendMessagesService": {
        "methods": {
            "GetActiveMessageSessions": {
                "version": 1
            },
            "GetRecentMessages": {
                "version": 1
            },
            "MarkOfflineMessagesRead": {
                "version": 1
            }
        }
    },
    "ITwoFactorService": {
        "methods": {
            "AddAuthenticator": {
                "version": 1
            },
            "RecoverAuthenticatorCommit": {
                "version": 1
            },
            "RecoverAuthenticatorContinue": {
                "version": 1
            },
            "RemoveAuthenticator": {
                "version": 1
            },
            "RemoveAuthenticatorViaChallengeStart": {
                "version": 1
            },
            "RemoveAuthenticatorViaChallengeContinue": {
                "version": 1
            },
            "FinalizeAddAuthenticator": {
                "version": 1
            },
            "QueryStatus": {
                "version": 1
            },
            "QueryTime": {
                "version": 1
            },
            "QuerySecrets": {
                "version": 1
            },
            "SendEmail": {
                "version": 1
            },
            "ValidateToken": {
                "version": 1
            },
            "CreateEmergencyCodes": {
                "version": 1
            },
            "DestroyEmergencyCodes": {
                "version": 1
            }
        }
    }
}

API_BASE_URL = 'https://api.steampowered.com'


class SteamMobile(object):
    session = None
    oauth = None
    steamid = None

    def __init__(self, username, password, login_mode='normal', email_code='', twofactor_code=''):
        mobile_auth = mobileauth.MobileAuth(username, password)

        try:
            if login_mode == 'normal':
                mobile_auth.login()
            elif login_mode == 'email':
                mobile_auth.login(email_code=email_code)
            elif login_mode == 'twofa':
                mobile_auth.login(twofactor_code=twofactor_code)

        except mobileauth.CaptchaRequired:
            raise CaptchaNotSupported("Captcha's are currently not supported. Please wait a few minutes before you try to login again.")
        except mobileauth.EmailCodeRequired:
            mobile_auth.login(email_code=email_code)
        except mobileauth.TwoFactorCodeRequired:
            mobile_auth.login(twofactor_code=twofactor_code)


        self.session = mobile_auth.session
        self.steamid = mobile_auth.steamid
        self.oauth = mobile_auth.oauth

    def refresh_session(self, oauth_token=None):
        oauth_token = oauth_token or self.oauth['oauth_token']
        response = self.api_request('IMobileAuthService', 'GetWGToken', {'access_token': oauth_token})
        try:
            data = json.loads(response)
        except Exception, e:
            raise SessionRefreshFailed(str(e))
        else:
            self.oauth['wgtoken'] = data['response']['token']
            self.oauth['wgtoken_secure'] = data['response']['token_secure']
            for domain in ['store.steampowered.com', 'help.steampowered.com', 'steamcommunity.com']:
                self.session.cookies.set('steamLogin', '%s||%s' % (self.steamid, self.oauth['wgtoken']), domain=domain,
                                         secure=False)
                self.session.cookies.set('steamLoginSecure', '%s||%s' % (self.steamid, self.oauth['wgtoken_secure']),
                                         domain=domain, secure=True)

    def _request(self, uri, data={}, return_including_status_code=False):
        headers = {
            'X-Requested-With': 'com.valvesoftware.android.steam.community',
            'User-agent': 'Mozilla/5.0 (Linux; U; Android 4.1.1; en-us; Google Nexus 4 - 4.1.1 - API 16 - 768x1280 Build/JRO03S)\
                            AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30'
        }

        try:
            response = self.session.post(uri, data=data, headers=headers)
        except requests.exceptions.RequestException as e:
            raise mobileauth.HTTPError(str(e))
        else:
            if return_including_status_code:
                return [response.status_code, response.text]
            else:
                return response.text

    def api_request(self, interface, method, data={}, return_including_status_code=False):
        if interface in API_ENDPOINTS.keys() and method in API_ENDPOINTS.get(interface).get('methods').keys():
            uri = '%s/%s/%s/v%s/' % (
                API_BASE_URL, interface, method, API_ENDPOINTS.get(interface).get('methods').get(method).get('version'))
            response = self._request(uri, data, return_including_status_code)
            return response
        else:
            raise APIEndpointNotFound('Endpoint %s.%s not found' % (interface, method))


class SteamMobileException(Exception):
    pass


class CaptchaNotSupported(SteamMobileException):
    pass


class SessionRefreshFailed(SteamMobileException):
    pass


class APIEndpointNotFound(SteamMobileException):
    pass