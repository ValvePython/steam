import requests
from bs4 import BeautifulSoup

class BrowserRequests(object):
    def __init__(self):
        self.session = None
        self.steam_id = None
        self.session_id = None

    def get_avatar_url(self, size=2):
        """Get URL to avatar picture

        :param size: possible values are ``0``, ``1``, or ``2`` corresponding to small, medium, large
        :type size: :class:`int`
        :return: url to avatar
        :rtype: :class:`str`
        :raises HTTPError: any problem with http request, timeouts, 5xx, 4xx etc
        """
        self.url = "https://steamcommunity.com/profiles/%s/edit/avatar"
        try:
            self.resp = self.session.get(self.url % self.steam_id,
                                     timeout=15,
                                     )
            self.req_bs = BeautifulSoup(self.resp.text)
            self.avatar_url = str(self.req_bs.find('div', {'class':'playerAvatar'}).find('img')['src'].split('.jpg')[0])
            sizes = {  # размеры картинок
                0: '',
                1: '_medium',
                2: '_full',
            }
        except requests.exceptions.RequestException as e:
            raise HTTPError(str(e))

        return self.avatar_url+sizes[size]+'.jpg'

    def set_avatar(self, avatar):
        """Set image to avatar picture

        :param avatar: bytes image
        :type avatar: :class:`bytes`
        :return: json response
        :rtype: :class:`dict`
        :raises HTTPError: any problem with http request, timeouts, 5xx, 4xx etc
        :raises AvatarRequiredNoSend: any problem with the format of the file being sent
        """
        self.url = "https://steamcommunity.com/actions/FileUploader/"
        try:
            self.resp = self.session.post(self.url,
                                    timeout=15,
                                    data={
                                         'type': 'player_avatar_image',
                                         'sId': self.steam_id,
                                         'sessionid': self.session_id,
                                         'doSub': 1,
                                         'json': 1
                                     },
                                    files={'avatar':avatar}
                                     ).json()
        except requests.exceptions.RequestException as e:
            raise HTTPError(str(e))
        if self.resp['success'] != True:
            raise AvatarRequiredNoSend
        return self.resp

class WebAuthException(Exception):
    pass

class HTTPError(WebAuthException):
    pass

class AvatarRequired(Exception):
    pass

class AvatarRequiredNoSend(AvatarRequired):
    pass