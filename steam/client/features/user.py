from steam.enums import EPersonaState
from steam.enums.emsg import EMsg
from steam.core.msg import MsgProto

class User(object):
    def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)

    def set_persona(self, state=None, name=None):
        """
        Set persona state and/or name

        :param state: persona state flag
        :type state: :class:`steam.enums.common.EPersonaState`
        :param name: profile name
        :type name: :class:`str`
        """
        if state is None and name is None:
            return

        message = MsgProto(EMsg.ClientChangeStatus)

        if state:
            if not isinstance(state, EPersonaState):
                raise ValueError("Expected state to be instance of EPersonaState")

            message.body.persona_state = state

        if name:
            message.body.player_name = name

        self.send(message)
