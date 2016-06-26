from steam.enums import EPersonaState
from steam.enums.emsg import EMsg
from steam.core.msg import MsgProto
from steam.util import proto_fill_from_dict

class User(object):
    persona_state = EPersonaState.Online    #: current persona state

    def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)

        self.on(self.EVENT_LOGGED_ON, self.__handle_set_persona)

    def __handle_set_persona(self):
        self.change_status(persona_state=self.persona_state)

    def change_status(self, **kwargs):
        """
        Set name, persona state, flags

        .. note::
            Changing persona state will also change :attr:`persona_state`

        :param persona_state: persona state (Online/Offlane/Away/etc)
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
