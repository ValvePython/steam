from weakref import WeakValueDictionary
from steam.client.user import SteamUser
from steam.enums import EPersonaState, EChatEntryType, EType, EClientUIMode
from steam.enums.emsg import EMsg
from steam.core.msg import MsgProto
from steam.utils.proto import proto_fill_from_dict

class User(object):
    EVENT_CHAT_MESSAGE = 'chat_message'
    """On new private chat message

    :param user: steam user
    :type user: :class:`.SteamUser`
    :param message: message text
    :type message: str
    """

    persona_state = EPersonaState.Online    #: current persona state
    user = None                             #: :class:`.SteamUser` instance once logged on
    current_games_played = []               #: :class:`list` of app ids currently being played

    def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)

        self._user_cache = WeakValueDictionary()

        self.on(self.EVENT_DISCONNECTED, self.__handle_disconnect)
        self.on(self.EVENT_LOGGED_ON, self.__handle_set_persona)
        self.on(EMsg.ClientPersonaState, self.__handle_persona_state)
        self.on(EMsg.ClientFriendMsgIncoming, self.__handle_message_incoming)
        self.on("FriendMessagesClient.IncomingMessage#1", self.__handle_message_incoming2)

    def __handle_message_incoming(self, msg):
        # old chat
        if msg.body.chat_entry_type == EChatEntryType.ChatMsg:
            user = self.get_user(msg.body.steamid_from)
            self.emit("chat_message", user, msg.body.message.decode('utf-8'))

    def __handle_message_incoming2(self, msg):
        # new chat
        if msg.body.chat_entry_type == EChatEntryType.ChatMsg and not msg.body.local_echo:
            user = self.get_user(msg.body.steamid_friend)
            self.emit("chat_message", user, msg.body.message)

    def __handle_disconnect(self):
        self.user = None
        self.current_games_played = []

    def __handle_set_persona(self):
        self.user = self.get_user(self.steam_id, False)

        if self.steam_id.type == EType.Individual and self.persona_state != EPersonaState.Offline:
            self.change_status(persona_state=self.persona_state)

    def __handle_persona_state(self, message):
        for friend in message.body.friends:
            steamid = friend.friendid

            if steamid in self._user_cache:
                suser = self._user_cache[steamid]
                suser._pstate = friend
                suser._pstate_ready.set()

    def change_status(self, **kwargs):
        """
        Set name, persona state, flags

        .. note::
            Changing persona state will also change :attr:`persona_state`

        :param persona_state: persona state (Online/Offline/Away/etc)
        :type persona_state: :class:`.EPersonaState`
        :param player_name: profile name
        :type player_name: :class:`str`
        :param persona_state_flags: persona state flags
        :type persona_state_flags: :class:`.EPersonaStateFlag`
        """
        if not kwargs: return

        self.persona_state = kwargs.get('persona_state', self.persona_state)

        message = MsgProto(EMsg.ClientChangeStatus)
        proto_fill_from_dict(message.body, kwargs)
        self.send(message)

    def request_persona_state(self, steam_ids, state_flags=863):
        """Request persona state data

        :param steam_ids: list of steam ids
        :type  steam_ids: :class:`list`
        :param state_flags: client state flags
        :type  state_flags: :class:`.EClientPersonaStateFlag`
        """
        m = MsgProto(EMsg.ClientRequestFriendData)
        m.body.persona_state_requested = state_flags
        m.body.friends.extend(steam_ids)
        self.send(m)

    def get_user(self, steam_id, fetch_persona_state=True):
        """Get :class:`.SteamUser` instance for ``steam id``

        :param steam_id: steam id
        :type steam_id: :class:`int`, :class:`.SteamID`
        :param fetch_persona_state: whether to request person state when necessary
        :type fetch_persona_state: :class:`bool`
        :return: SteamUser instance
        :rtype: :class:`.SteamUser`
        """
        steam_id = int(steam_id)
        suser = self._user_cache.get(steam_id, None)

        if suser is None:
            suser = SteamUser(steam_id, self)
            self._user_cache[steam_id] = suser

            if fetch_persona_state:
                suser.refresh(wait=False)

        return suser

    def games_played(self, app_ids):
        """
        Set the apps being played by the user

        :param app_ids: a list of application ids
        :type app_ids: :class:`list`

        These app ids will be recorded in :attr:`current_games_played`.
        """
        if not isinstance(app_ids, list):
            raise ValueError("Expected app_ids to be of type list")

        self.current_games_played = app_ids = list(map(int, app_ids))

        self.send(MsgProto(EMsg.ClientGamesPlayed),
                  {'games_played': [{'game_id': app_id} for app_id in app_ids]}
                  )

    def set_ui_mode(self, uimode):
        """
        Set UI mode. Show little icon next to name in friend list. (e.g phone, controller, other)

        :param uimode: UI mode integer
        :type  uimode: :class:`EClientUIMode`

        These app ids will be recorded in :attr:`current_games_played`.
        """
        self.send(MsgProto(EMsg.ClientCurrentUIMode), {'uimode': EClientUIMode(uimode)})
