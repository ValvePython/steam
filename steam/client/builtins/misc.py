"""
Various features that don't have a category
"""
from steam.core.msg import MsgProto
from steam.enums.emsg import EMsg


class Misc(object):
    def __init__(self, *args, **kwargs):
        super(Misc, self).__init__(*args, **kwargs)

    def games_played(self, app_ids):
        """
        Set the application being played by the user

        :param app_ids: a list of application ids
        :type app_ids: :class:`list`
        """
        if not isinstance(app_ids, list):
            raise ValueError("Expected app_ids to be of type list")

        app_ids = map(int, app_ids)

        message = MsgProto(EMsg.ClientGamesPlayed)
        GamePlayed = message.body.GamePlayed

        message.body.games_played.extend(map(lambda x: GamePlayed(game_id=x), app_ids))

        self.send(message)
