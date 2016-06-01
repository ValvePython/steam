import json

from guard import *
from mobileauth import MobileAuth

class MobileAuthenticator:
  def __init__(self, username, password, authenticatorCredentials=False):
    self.username = username
    self.password = password
    self.ready    = None
    self.mobile   = MobileAuth(username, password)
    self.credentials = authenticatorCredentials or { }
  
  def login(self):
    if self.ready != None:
      return False
    
    if 'secret' in self.credentials.keys():
      code = generate_twofactor_code(self.credentials.get('secret'))
      self.mobile.login(twofactor_code=code)
      return True
    else:
      try:
        self.mobile.login()
      except EmailCodeRequired:
        raise AuthenticatorAlreadyActive('Two factor authentication already active')
      except TwoFactorCodeRequired
        raise AuthenticatorAlreadyActive('Two factor authentication already active')
      else:
        self.ready = False
        return True
      
  def addAuthenticator(self):
    if self.ready != False:
      return None
      
      
    data = {
     'steamid': self.mobile.steamid,
     'sms_phone_id': 1,
     'access_token': self.mobile.oauth['oauth_token'],
     'authenticator_time': get_time_offset(),
     'authenticator_type': 1,
     'device_identifier': generate_device_id(self.mobile.steamid)
    }
      
    response = self.mobile.request('https://api.steampowered.com/ITwoFactorService/AddAuthenticator/v1/', data)
    if response.status_code == 200:
      responseData = json.loads(response.text)
      self.credentials = responseData['response']
      self.credentials['secret'] = self.credentials['uri'].split('?secret=')[1].split('&issuer')[0]
      return True
    else:
      return [False, responseData]
  
  def finalizeAuthenticator(self, smsCode=None, tries=1):
    if not smsCode or self.ready != False:
      return None
      
    timestamp = get_time_offset()
      
    data = {
      'steamid': self.mobile.steamid,
      'access_token': self.mobile.oauth['oauth_token'],
      'authenticator_time': timestamp,
      'authenticator_code': generate_twofactor_code_for_time(self.credentials['secret'], timestamp),
      'activation_code': smsCode
    }
    response = self.mobile.request('https://api.steampowered.com/ITwoFactorService/FinalizeAddAuthenticator/v1/', data)
    if response.status_code == 200:
      responseData = json.loads(response.text)
      if responseData['success']:
        return True
      else:
        if responseData['want_more'] and tries < 30:
          return self.finalizeAuthenticator(smsCode, tries)
        else:
          return False
    else:
      return False
      
class MobileAuthenticatorException(Exception):
  pass

class AuthenticatorAlreadyActive(MobileAuthenticatorException)
  pass
