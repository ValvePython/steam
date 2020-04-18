import logging
from six import itervalues
from eventemitter import EventEmitter
from steam.steamid import SteamID, intBase
from steam.enums import EResult, EFriendRelationship
from steam.enums.emsg import EMsg
from steam.core.msg import MsgProto
from steam.client.user import SteamUser


class Friends(object):
    def __init__(self, *args, **kwargs):
        super(Friends, self).__init__(*args, **kwargs)

        #: :class:`.SteamFriendlist` instance
        self.friends = SteamFriendlist(self, logger_name="%s.friends" % self.__class__.__name__)

class SteamFriendlist(EventEmitter):
    """SteamFriendlist is an object that keeps state of user's friend list.
    It's essentially a :class:`list` of :class:`.SteamUser`.
    You can iterate over it, check if it contains a particular ``steam id``,
    or get :class:`.SteamUser` for a ``steam id``.
    """
    EVENT_READY = 'ready'
    """Friend list is ready for use
    """
    EVENT_FRIEND_INVITE = 'friend_invite'
    """New or existing friend invite

    :param user: steam user instance
    :type user: :class:`.SteamUser`
    """
    EVENT_FRIEND_NEW = 'friend_new'
    """Friendship established (after being accepted, or accepting)

    :param user: steam user instance
    :type user: :class:`.SteamUser`
    """
    EVENT_FRIEND_REMOVED = 'friend_removed'
    """No longer a friend (removed by either side)

    :param user: steam user instance
    :type user: :class:`.SteamUser`
    """
    EVENT_FRIEND_ADD_RESULT = 'friend_add_result'
    """Result response after adding a friend

    :param eresult: result
    :type eresult: :class:`.EResult`
    :param steam_id: steam id
    :type steam_id: :class:`.SteamID`
    """

    ready = False  #: indicates whether friend list is ready for use

    def __init__(self, client, logger_name='SteamFriendList'):
        self._LOG = logging.getLogger(logger_name)
        self._fr = {}
        self._steam = client

        self._steam.on(EMsg.ClientAddFriendResponse, self._handle_add_friend_result)
        self._steam.on(EMsg.ClientFriendsList, self._handle_friends_list)
        self._steam.on(self._steam.EVENT_DISCONNECTED, self._handle_disconnect)

    def emit(self, event, *args):
        if event is not None:
            self._LOG.debug("Emit event: %s" % repr(event))
        EventEmitter.emit(self, event, *args)

    def _handle_disconnect(self):
        self.ready = False
        self._fr.clear()

    def _handle_add_friend_result(self, message):
        eresult = EResult(message.body.eresult)
        steam_id = SteamID(message.body.steam_id_added)
        self.emit(self.EVENT_FRIEND_ADD_RESULT, eresult, steam_id)

    def _handle_friends_list(self, message):
        incremental = message.body.bincremental
        if incremental == False:
            self._fr.clear()

        steamids_to_check = set()

        # update internal friends list
        for friend in message.body.friends:
            steamid = SteamID(friend.ulfriendid)

            if steamid.type != steamid.EType.Individual:
                continue

            suser = self._steam.get_user(steamid, False)
            rel = EFriendRelationship(friend.efriendrelationship)

            if steamid not in self._fr and rel != EFriendRelationship.NONE: # 0
                self._fr[steamid] = suser
                suser.relationship = rel
                steamids_to_check.add(steamid)

                if rel in (2,4):  # RequestRecipient = 2, RequestInitiator = 4
                    if rel == EFriendRelationship.RequestRecipient:
                        self.emit(self.EVENT_FRIEND_INVITE, suser)
            else:
                oldrel, suser.relationship = suser.relationship, rel

                if rel == EFriendRelationship.NONE:
                    suser = self._fr.pop(steamid, None)
                    if suser and oldrel not in (EFriendRelationship.Ignored, 0):
                        self.emit(self.EVENT_FRIEND_REMOVED, suser)
                elif oldrel in (2,4) and rel == EFriendRelationship.Friend:
                    self.emit(self.EVENT_FRIEND_NEW, suser)

        # request persona state for any new entries
        if steamids_to_check:
            self._steam.request_persona_state(steamids_to_check)

        if not self.ready:
            self.ready = True
            self.emit(self.EVENT_READY)

    def __repr__(self):
        return "<%s %d users>" % (
            self.__class__.__name__,
            len(self._fr),
            )

    def __len__(self):
        return len(self._fr)

    def __iter__(self):
        return itervalues(self._fr)

    def __list__(self):
        return list(iter(self))

    def __getitem__(self, key):
        if isinstance(key, SteamUser):
            key = key.steam_id
        return self._fr[key]

    def __contains__(self, friend):
        if isinstance(friend, SteamUser):
            friend = friend.steam_id
        return friend in self._fr

    def add(self, steamid_or_accountname_or_email):
        """
        Add/Accept a steam user to be your friend.
        When someone sends you an invite, use this method to accept it.

        :param steamid_or_accountname_or_email: steamid, account name, or email
        :type steamid_or_accountname_or_email: :class:`int`, :class:`.SteamID`, :class:`.SteamUser`, :class:`str`

        .. note::
            Adding by email doesn't not work. It's only mentioned for the sake of completeness.
        """
        m = MsgProto(EMsg.ClientAddFriend)

        if isinstance(steamid_or_accountname_or_email, (intBase, int)):
            m.body.steamid_to_add = steamid_or_accountname_or_email
        elif isinstance(steamid_or_accountname_or_email, SteamUser):
            m.body.steamid_to_add = steamid_or_accountname_or_email.steam_id
        else:
            m.body.accountname_or_email_to_add = steamid_or_accountname_or_email

        self._steam.send_job(m)

    def remove(self, steamid):
        """
        Remove a friend

        :param steamid: their steamid
        :type steamid: :class:`int`, :class:`.SteamID`, :class:`.SteamUser`
        """
        if isinstance(steamid, SteamUser):
            steamid = steamid.steam_id

        self._steam.send(MsgProto(EMsg.ClientRemoveFriend), {'friendid': steamid})

    def block(self, steamid):
        """
        Block Steam user

        :param steamid: their steamid
        :type  steamid: :class:`int`, :class:`.SteamID`, :class:`.SteamUser`
        :return: result
        :rtype: :class:`EResult`
        """
        if isinstance(steamid, SteamUser):
            steamid = steamid.steam_id
        elif not isinstance(steamid, SteamID):
            steamid = SteamID(steamid)

        resp = self._steam.send_um_and_wait("Player.IgnoreFriend#1",
                                            {"steamid": steamid},
                                            timeout=10)

        if not resp:
            return EResult.Timeout
        elif resp.header.eresult == EResult.OK:
            if steamid not in self._fr:
                self._fr[steamid] = self._steam.get_user(steamid, False)
            self._fr[steamid].relationship = EFriendRelationship(resp.body.friend_relationship)

        return resp.header.eresult

    def unblock(self, steamid):
        """
        Unblock Steam user

        :param steamid: their steamid
        :type  steamid: :class:`int`, :class:`.SteamID`, :class:`.SteamUser`
        :return: result
        :rtype: :class:`EResult`
        """
        if isinstance(steamid, SteamUser):
            steamid = steamid.steam_id
        elif not isinstance(steamid, SteamID):
            steamid = SteamID(steamid)

        resp = self._steam.send_um_and_wait("Player.IgnoreFriend#1",
                                            {"steamid": steamid, "unignore": True},
                                            timeout=10)

        if not resp:
            return EResult.Timeout
        elif resp.header.eresult == EResult.OK:
            if steamid in self._fr:
                self._fr[steamid].relationship = EFriendRelationship(resp.body.friend_relationship)

        return resp.header.eresult
