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
        if not wait_pstate or self._pstate_ready.wait(timeout=5):
            if self._pstate is None and wait_pstate:
                self._steam.request_persona_state([self.steam_id])
                self._pstate_ready.wait(timeout=5)

            if self._pstate and self._pstate.HasField(field_name):
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
        self._steam.send(MsgProto(EMsg.ClientFriendMsg), {
            'steamid': self.steam_id,
            'chat_entry_type': EChatEntryType.ChatMsg,
            'message': message.encode('utf8'),
            })
