import logging
from eventemitter import EventEmitter
from steam.steamid import SteamID, intBase
from steam.enums import EResult, EFriendRelationship, EPersonaState
from steam.enums.emsg import EMsg
from steam.core.msg import MsgProto


class Friends(object):
    def __init__(self, *args, **kwargs):
        super(Friends, self).__init__(*args, **kwargs)

        #: SteamFriendlist instance
        self.friends = SteamFriendlist(self)

class SteamFriendlist(EventEmitter):
    _LOG = logging.getLogger('SteamClient.friends')

    def __init__(self, client):
        self._fr = {}
        self._steam = client

        self._steam.on(EMsg.ClientAddFriendResponse, self._handle_add_friend_result)
        self._steam.on(EMsg.ClientFriendsList, self._handle_friends_list)
        self._steam.on(EMsg.ClientPersonaState, self._handle_persona_state)

    def emit(self, event, *args):
        if event is not None:
            self._LOG.debug("Emit event: %s" % repr(event))
        EventEmitter.emit(self, event, *args)

    def _handle_add_friend_result(self, message):
        eresult = EResult(message.body.eresult)
        steam_id = SteamID(message.body.steam_id_added)
        self.emit("friend_add_result", eresult, steam_id)

    def _handle_friends_list(self, message):
        incremental = message.body.bincremental
        if incremental == False:
            self._fr.clear()

        pstate_check = set()

        # update internal friends list
        for friend in message.body.friends:
            steamid = friend.ulfriendid
            rel = EFriendRelationship(friend.efriendrelationship)

            if steamid not in self._fr:
                suser = SteamUser(steamid, rel)
                self._fr[suser] = suser

                if rel in (2,4):
                    if incremental == False:
                        pstate_check.add(steamid)

                    if rel == EFriendRelationship.RequestRecipient:
                        self.emit('friend_invite', suser)
            else:
                oldrel = self._fr[steamid]._data['relationship']
                self._fr[steamid]._data['relationship'] = rel

                if rel == EFriendRelationship.No:
                    self.emit('friend_removed', self._fr.pop(steamid))
                elif oldrel in (2,4) and rel == EFriendRelationship.Friend:
                    self.emit('friend_new', self._fr[steamid])

        # request persona state for any new entries
        if pstate_check:
            m = MsgProto(EMsg.ClientRequestFriendData)
            m.body.persona_state_requested = 4294967295  # request all possible flags
            m.body.friends.extend(pstate_check)
            self._steam.send(m)

    def _handle_persona_state(self, message):
        for friend in message.body.friends:
            steamid = friend.friendid

            if steamid == self._steam.steam_id:
                continue

            if steamid in self._fr:
                self._fr[steamid]._data['pstate'] = friend

    def __repr__(self):
        return "<%s %d users>" % (
            self.__class__.__name__,
            len(self._fr),
            )

    def __len__(self):
        return len(self._fr)

    def __iter__(self):
        return iter(self._fr)

    def __list__(self):
        return list(self._fr)

    def __getitem__(self, key):
        return self._fr[key]

    def __contains__(self, friend):
        return friend in self._fr

    def add(self, steamid_or_accountname_or_email):
        """
        Add/Accept a steam user to be your friend.
        When someone sends you an invite, use this method to accept it.

        :param steamid_or_accountname_or_email: steamid, account name, or email
        :type steamid_or_accountname_or_email: :class:`int`, :class:`steam.steamid.SteamID`, :class:`SteamUser`, :class:`str`

        .. note::
            Adding by email doesn't not work. It's only mentioned for the sake of completeness.
        """
        m = MsgProto(EMsg.ClientAddFriend)

        if isinstance(steamid_or_accountname_or_email, (intBase, int)):
            m.body.steamid_to_add = steamid_or_accountname_or_email
        else:
            m.body.accountname_or_email_to_add = steamid_or_accountname_or_email

        self._steam.send(m)

    def remove(self, steamid):
        """
        Remove a friend

        :param steamid: their steamid
        :type steamid: :class:`int`, :class:`steam.steamid.SteamID`, :class:`SteamUser`
        """
        m = MsgProto(EMsg.ClientRemoveFriend)
        m.body.friendid = steamid
        self._steam.send(m)

class SteamUser(intBase):
    def __new__(cls, steam64, *args, **kwargs):
        return super(SteamUser, cls).__new__(cls, steam64)

    def __init__(self, steam64, rel):
        self._data = {
            'relationship': EFriendRelationship(rel)
        }

    @property
    def steamid(self):
        """SteamID instance

        :rtype: :class:`steam.steamid.SteamID`
        """
        return SteamID(int(self))

    @property
    def relationship(self):
        """Current relationship with the steam user

        :rtype: :class:`steam.enums.common.EFriendRelationship`
        """
        return self._data['relationship']

    def get_persona_state_value(self, field_name):
        """Get a value for field in ``CMsgClientPersonaState.Friend``

        :param field_name: see example list below
        :type field_name: :class:`str`
        :return: value for the field, or ``None`` if not available
        :rtype: :class:`None`, :class:`int`, :class:`str`, :class:`bytes`, :class:`bool`

        Examples:
         - game_played_app_id
         - last_logoff
         - last_logon
         - game_name
         - avatar_hash
         - facebook_id
         ...

        """
        pstate = self._data.get('pstate', None)
        if pstate is None or not pstate.HasField(field_name):
            return None
        return getattr(pstate, field_name)

    @property
    def name(self):
        """Name of the steam user, or ``None`` if it's not available

        :rtype: :class:`str`, :class:`None`
        """
        return self.get_persona_state_value('player_name')

    @property
    def state(self):
        """State of the steam user

        :rtype: :class:`steam.enums.common.EPersonaState`
        """
        state = self.get_persona_state_value('persona_state')
        if state:
            return EPersonaState(state)
        return EPersonaState.Offline

    def get_avatar_url(self, size=2):
        """Get url to the steam avatar

        :param size: possible values are ``0``, ``1``, or ``2`` corresponding to small, medium, large
        :type size: :class:`int`
        :return: url to avatar
        :rtype: :class:`str`
        """
        ahash = self.get_persona_state_value('avatar_hash')
        if ahash is None:
            return None

        sizes = {
            0: '',
            1: '_medium',
            2: '_full',
        }
        url = "http://cdn.akamai.steamstatic.com/steamcommunity/public/images/avatars/%s/%s%s.jpg"
        ahash = binascii.hexlify(persona_state_value.avatar_hash).decode('ascii')

        return url % (ahash[:2], ahash, sizes[size])

    def __repr__(self):
        return "<%s (%s) %s %s>" % (
            self.__class__.__name__,
            int(self) if self.name is None else repr(self.name),
            self.relationship.name,
            self.state.name,
            )
