# -*- coding: utf-8 -*-
"""
Wrapping methods for `ISteamWebUserPresenceOAuth` and `Polling` functionality

Example usage:

.. code:: python
    import steam.webauth
    import steam.webpresence
    webAuth = steam.webauth.MobileWebAuth('username', 'password')
    webAuth.login()

    def my_callback(messages):
        for message in messages:
            print '[%s] %s from %s' % (message.timestamp, message.type, message.steamid_from.as_64)

    webPresence = steam.webpresence.WebUserPresence(webAuth)
    webPresence.logon()
    webPresence.start_polling(my_callback)
    print 'Started polling'
"""
import threading
import requests

from steam.webauth import MobileWebAuth
from steam import SteamID

DEFAULT_MOBILE_HEADERS = {
    'X-Requested-With': 'com.valvesoftware.android.steam.community',
    'User-agent': 'Mozilla/5.0 (Linux; U; Android 4.1.1; en-us; Google Nexus 4 - 4.1.1 - API 16 - 768x1280 Build/JRO03S) \
     AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30'
}

API_BASE               = 'https://api.steampowered.com'

DEFAULT_TIMEOUT        = 30

PERSONA_STATES         = ['Offline', 'Online', 'Busy', 'Away', 'Snooze', 'Looking to trade', 'Looking to play']

class WebUserPresence:
    """
    Wrapping methods for `ISteamWebUserPresenceOAuth` and `Polling` functionality
    """
    _loggedon       = False
    _timeout        = None

    _oauth_token    = None
    _session        = None

    _steamid        = None
    _umqid          = None
    _message_base   = None

    def __init__(self, mobile_web_auth, timeout=None):
        if not isinstance(mobile_web_auth, MobileWebAuth):
            raise InvalidInstanceSupplied('The instance supplied as parameter is no valid instance of `MobileWebAuth`.')

        if not mobile_web_auth.complete:
            raise InstanceNotReady('Please make sure your `MobileWebAuth` instance is logged in.')

        self._timeout       = timeout
        self._oauth_token   = mobile_web_auth.oauth_token
        self._session       = mobile_web_auth.session

    def _request(self, uri, data, timeout=None):
        """
        HTTP Request
        :param uri: URI to be requested
        :param data: Data to be delivered
        :param timeout: HTTP timeout
        :return: `requests.Response`
        """
        timeout = timeout or self._timeout or DEFAULT_TIMEOUT
        return self._session.post(uri, data=data, headers=DEFAULT_MOBILE_HEADERS, timeout=timeout)

    def _call(self, method, data, timeout=None):
        """
        Calling an `ISteamWebUserPresenceOAuth` api method
        :param method: Method to be called
        :param data: Data to be delivered
        :param timeout: HTTP timeout
        :return: If successful, response as tuple, otherwise exceptions are thrown
        """
        uri = '%s/ISteamWebUserPresenceOAuth/%s/v1/' % (API_BASE, method)

        try:
            response = self._request(uri, data, timeout=timeout)
        except requests.exceptions.ReadTimeout:
            raise HTTPError('Timeout')

        if response.status_code == 401:
            raise NotAuthorized('Not authorized. Please check your OAuth token and verify your `MobileWebAuth` login.')
        elif response.status_code != 200:
            raise HTTPError('HTTP request failed. Status code: %s' % response.status_code)

        if self._loggedon:
            self._message_base += 1

        try:
            json_response = response.json()
        except:
            raise ValueError('Could not build json_response')
        else:
            return json_response

    def logon(self):
        """
        Sends logon to the api
        :return: True if successful. Raises an `LogonFailed` exception otherwise
        """
        login_data = {
            'access_token': self._oauth_token
        }
        response = self._call('Logon', login_data)
        if response.get('error') == 'OK':
            self._steamid       = SteamID(response.get('steamid'))
            self._umqid         = response.get('umqid')
            self._message_base  = response.get('message')

            self._loggedon      = True
            return True
        else:
            raise LogonFailed('Logon failed. Please check your OAuth token and verify your `MobileWebAuth` login.')

    def logoff(self):
        """
        Sends logoff to the api
        :return: True if logoff was successful, False otherwise.
        """
        response = self._call('Logoff', self._build_call_data({}), True)
        self._loggedon = False
        return response.get('error') == 'OK' or False

    def poll(self):
        """
        Starts an poll request
        :return: Full response as Tuple
        """
        poll_data = {
            'pollid': 0,
            'sectimeout': 5,
            'secidletime': 0,
            'use_accountids': 1
        }
        response = self._call('Poll', self._build_call_data(poll_data, True), timeout=60)
        if response.get('error') == 'OK':
            return response
        else:
            raise PollCreationFailed(response.get('error'))

    def start_polling(self, callback):
        """
        Creates an instance of `WebPolling` and starts the thread
        :param callback: Function reference for handling `WebPollMessages`
        :return: True
        """
        web_polling = self._spawn_web_polling(callback)
        web_polling.start()
        return True

    def stop_polling(self):
        """
        Stops the active `WebPolling`
        :return: True, False.
        """
        return self._kill_web_polling()

    def message(self, steamid, text):
        """
        Delivers a steam message
        :param steamid: SteamID64 of the target user
        :param text: Message to deliver
        :return: True if deliver was successful, False otherwise
        """
        message_data = self._build_call_data({
            'text': text,
            'type': 'saytext',
            'steamid_dst': steamid
        })
        response = self._call('Message', message_data)
        return response.get('error') == 'OK' or False

    def _spawn_web_polling(self, callback):
        """
        Spawns a `WebPolling` instance
        :param callback: A method reference for handling incoming `WebPollMessages`
        :return: Instance reference
        """
        self._web_polling = WebPolling(self, callback)
        return self._web_polling

    def _kill_web_polling(self):
        """
        Stops the run() method of WebPolling after the current poll request
        :return: True if `_web_polling` is spawned and could be stopped, False otherwise
        """
        if getattr(self, '_web_polling'):
            self._web_polling._active = False
            return True
        return False

    def _prep_messages(self, messages):
        """
        Prepares incoming raw `WebPolling` messages by creating `WebPollMessage` instances
        :param messages: raw `WebPolling` messages
        :return: List of `WebPollMessages` instances
        """
        prepped_messages    = [ ]
        for message in messages:
            prepped_messages.append(WebPollMessage(message, self))
        return prepped_messages

    def _build_call_data(self, data, set_message_base=False):
        """
        Builds the data for `_call`'s
        :param data: Data to deliver as Tuple
        :param set_message_base: True, False. Only required for calls where `message` has to be set
        :return: Prepared call data
        """
        base_data = {
            'umqid': self._umqid,
            'access_token': self._oauth_token
        }
        if set_message_base:
            base_data.__setitem__('message', self._message_base)

        for key in data:
            base_data.__setitem__(key, data.get(key))

        return base_data

class WebPolling(threading.Thread):
    """
    Threaded class for `Polling`
    """
    _active             = True
    _web_user_presence  = None
    _callback           = None

    def __init__(self, web_user_presence, callback):
        threading.Thread.__init__(self)

        if not isinstance(web_user_presence, WebUserPresence):
            raise InvalidInstanceSupplied('The instance supplied as parameter is no valid instance of `WebUserPresence`.')

        if not web_user_presence._loggedon:
            raise InstanceNotReady('The `WebUserPresence` has to be logged on.')

        self._web_user_presence = web_user_presence
        self._callback          = callback

        self.setDaemon(False)

    def run(self):
        """
        Sends HTTP requests while class is `_active` and calls a specified callback
        :return:
        """
        while self._active:
            try:
                response = self._web_user_presence.poll()
            except PollCreationFailed:
                """
                Ignore timeout exception
                """
                pass
            except HTTPError:
                """
                Ignore http exceptions
                """
                pass
            else:
                prepped_messages = self._web_user_presence._prep_messages(response.get('messages'))
                if self._callback:
                    self._callback(prepped_messages)

class WebPollMessage(object):
    """
    Class for proper handling of polling messages
    """
    complete            = False

    _web_user_presence  = None

    timestamp           = 0
    type                = None
    steamid_from        = SteamID()

    text                = None

    persona_state       = 0
    persona_name        = None
    status_flags        = None

    _answerable         = False
    _full_data          = None

    def __init__(self, message, web_user_presence):
        if not isinstance(web_user_presence, WebUserPresence):
            raise InvalidInstanceSupplied('The instance supplied as parameter is no valid instance of `WebUserPresence`.')

        if not web_user_presence._loggedon:
            raise InstanceNotReady('The `WebUserPresence` has to be logged on.')

        self._full_data     = message

        self._web_user_presence = web_user_presence

        self.timestamp      = message.get('utc_timestamp')
        self.type           = message.get('type')
        self.steamid_from   = SteamID(message.get('accountid_from'))

        if self.type == 'typing':
            self._answerable = True
        elif self.type == 'saytext':
            self._answerable = True
            self.text        = message.get('text')
        elif self.type == 'personastate':
            self.persona_name = message.get('persona_name')
            self.persona_state = message.get('persona_state')
            self.status_flags = message.get('status_flags')

    def answer(self, message):
        """
        If the current message is `_answerable` ( current message has something to do with the steam chat ) an
        answer can be sent
        :param message: Message to be delivered
        :return: True if message could be delivered, False otherwise
        """
        if not self._answerable:
            return False
        self._web_user_presence.message(self.steamid_from.as_64, message)
        return True

    def persona_state_to_str(self):
        """
        Returns the `persona_state` as string
        :return: `persona_state` as String or False if `persona_state` is not available
        """
        if self.persona_state:
            return PERSONA_STATES.__getitem__(self.persona_state)
        return False

class WebUserPresenceException(Exception):
    pass

class InvalidInstanceSupplied(WebUserPresenceException):
    pass

class InstanceNotReady(WebUserPresenceException):
    pass

class NotAuthorized(WebUserPresenceException):
    pass

class LogonFailed(WebUserPresenceException):
    pass

class PollCreationFailed(WebUserPresenceException):
    pass

class HTTPError(WebUserPresenceException):
    pass