from datetime import datetime
from binascii import hexlify
from gevent.event import Event
from steam.steamid import SteamID
from steam.enums import EFriendRelationship, EPersonaState, EChatEntryType
from steam.enums.emsg import EMsg
from steam.core.msg import MsgProto

class SteamUser(object):
    """Holds various functionality and data related to a steam user
    """
    _pstate = None
    steam_id = SteamID()  #: steam id
    relationship = EFriendRelationship.NONE   #: friendship status

    def __init__(self, steam_id, steam):
        self._pstate_ready = Event()
        self._steam = steam
        self.steam_id = SteamID(steam_id)

    def __repr__(self):
        return "<%s(%s, %s)>" % (
            self.__class__.__name__,
            str(self.steam_id),
            self.state,
            )

    def get_ps(self, field_name, wait_pstate=True):
        """Get property from PersonaState

        `See full list of available fields_names <https://github.com/ValvePython/steam/blob/fa8a5127e9bb23185483930da0b6ae85e93055a7/protobufs/steammessages_clientserver_friends.proto#L125-L153>`_
        """
        if not wait_pstate or self._pstate_ready.wait(timeout=5):
            if self._pstate is None and wait_pstate:
                self._steam.request_persona_state([self.steam_id])
                self._pstate_ready.wait(timeout=5)

            return getattr(self._pstate, field_name)
        return None

    @property
    def last_logon(self):
        """:rtype: :class:`datetime`, :class:`None`"""
        ts = self.get_ps('last_logon')
        return datetime.utcfromtimestamp(ts) if ts else None

    @property
    def last_logoff(self):
        """:rtype: :class:`datetime`, :class:`None`"""
        ts = self.get_ps('last_logoff')
        return datetime.utcfromtimestamp(ts) if ts else None

    @property
    def name(self):
        """Name of the steam user, or ``None`` if it's not available

        :rtype: :class:`str`, :class:`None`
        """
        return self.get_ps('player_name')

    @property
    def state(self):
        """Personsa state (e.g. Online, Offline, Away, Busy, etc)

        :rtype: :class:`.EPersonaState`
        """
        state = self.get_ps('persona_state', False)
        return EPersonaState(state) if state else EPersonaState.Offline

    @property
    def rich_presence(self):
        """Contains Rich Presence key-values

        :rtype: dict
        """
        kvs = self.get_ps('rich_presence')
        data = {}

        if kvs:
            for kv in kvs:
                data[kv.key] = kv.value

        return data

    def get_avatar_url(self, size=2):
        """Get URL to avatar picture

        :param size: possible values are ``0``, ``1``, or ``2`` corresponding to small, medium, large
        :type size: :class:`int`
        :return: url to avatar
        :rtype: :class:`str`
        """
        hashbytes = self.get_ps('avatar_hash')

        if hashbytes != "\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000":
            ahash = hexlify(hashbytes).decode('ascii')
        else:
            ahash = 'fef49e7fa7e1997310d705b2a6158ff8dc1cdfeb'

        sizes = {
            0: '',
            1: '_medium',
            2: '_full',
        }
        url = "http://cdn.akamai.steamstatic.com/steamcommunity/public/images/avatars/%s/%s%s.jpg"

        return url % (ahash[:2], ahash, sizes[size])

    def send_message(self, message):
        """Send chat message to this steam user

        :param message: message to send
        :type message: str
        """
        # new chat
        if self._steam.chat_mode == 2:
            self._steam.send_um("FriendMessages.SendMessage#1", {
                'steamid': self.steam_id,
                'message': message,
                'chat_entry_type': EChatEntryType.ChatMsg,
                })
        # old chat
        else:
            self._steam.send(MsgProto(EMsg.ClientFriendMsg), {
                'steamid': self.steam_id,
                'chat_entry_type': EChatEntryType.ChatMsg,
                'message': message.encode('utf8'),
                })
