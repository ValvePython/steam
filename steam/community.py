# -*- coding: utf-8 -*-

"""
This module contains methods for working with Community Steam

Example usage:
.. code:: python
    import steam.webauth as wa
    import steam.community

    client = wa.WebAuth('login', 'password')
    client.login()

    co_client = steam.community.SteamCommunityClient(client=client)
    result = co_client.set_avatar(avatar=open('image.jpg', 'rb').read())

"""

import requests
from bs4 import BeautifulSoup
from steam.webauth import WebAuthException, HTTPError

class SteamCommunityClient():
    def __init__(self, client):
        self.client = client
        self.session = self.client.session
        self.steam_id = self.client.steam_id
        self.session_id = self.client.session_id
        self.cookies = self.client.session.cookies

    def get_avatar_url(self, size=2) -> str:
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

    def set_avatar(self, avatar: bytes) -> dict:
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


class AvatarRequired(Exception):
    pass

class AvatarRequiredNoSend(AvatarRequired):
    pass