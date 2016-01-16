import logging
import gevent
from steam.util.events import EventEmitter
from steam.enums.emsg import EMsg
from steam.enums import EResult
from steam.core.msg import MsgProto
from steam.core.cm import CMClient
from steam import SteamID
from steam.client.jobs import JobManager

logger = logging.getLogger("SteamClient")


class SteamClient(EventEmitter):
    def __init__(self):
        self.cm = CMClient()
        self.job = JobManager(self)

        # re-emit all events from CMClient
        self.cm.on(None, self.emit)

        # register listners
        self.on(EMsg.ClientLogOnResponse, self._handle_logon)
        self.on("disconnected", self._handle_disconnect)

        self.logged_on = False

    def emit(self, event, *args):
        if event is not None:
            logger.debug("Emit event: %s" % repr(event))
        super(SteamClient, self).emit(event, *args)

    @property
    def steam_id(self):
        return self.cm.steam_id
    @property

    def connected(self):
        return self.cm.connected

    def connect(self):
        self.cm.connect()

    def disconnect(self):
        self.cm.disconnect()

    def _handle_disconnect(self):
        self.logged_on = False

    def _handle_logon(self, msg):
        result = EResult(msg.body.eresult)

        if result == EResult.OK:
            self.logged_on = True
            self.emit("logged_on")
            return

        # CM kills the connection on error anyway
        self.disconnect()

        if result in (EResult.AccountLogonDenied,
                        EResult.AccountLoginDeniedNeedTwoFactor,
                        EResult.TwoFactorCodeMismatch,
                        ):
            self.emit("auth_code_required", result)
        else:
            self.emit("error", result)

    def send(self, message):
        if not self.connected:
            raise RuntimeError("Cannot send message while not connected")

        self.cm.send_message(message)

    def _pre_login(self):
        if self.logged_on:
            logger.debug("Trying to login while logged on???")
            raise RuntimeError("Already logged on")

        if not self.connected:
            self.connect()

        if not self.cm.channel_secured:
            self.wait_event("channel_secured")

    def anonymous_login(self):
        logger.debug("Attempting Anonymous login")

        self._pre_login()

        message = MsgProto(EMsg.ClientLogon)
        message.header.steamid = SteamID(type='AnonUser', universe='Public')
        message.body.protocol_version = 65575
        self.send(message)

    def login(self, username, password, auth_code=None, two_factor_code=None, remember=False):
        logger.debug("Attempting login")

        self._pre_login()

        message = MsgProto(EMsg.ClientLogon)
        message.header.steamid = SteamID(type='Individual', universe='Public')
        message.body.protocol_version = 65575
        message.body.client_package_version = 1771
        message.body.client_os_type = 13
        message.body.client_language = "english"

        message.body.account_name = username
        message.body.password = password

        if auth_code:
            message.body.auth_code = auth_code
        if two_factor_code:
            message.body.two_factor_code = two_factor_code

        self.send(message)

    def logout(self):
        if self.logged_on:
            self.logged_on = False
            self.send(MsgProto(EMsg.ClientLogOff))
            self.wait_event('disconnected')

    def run_forever(self):
        while True:
            gevent.sleep(300)

    def games_played(self, app_ids):
        if not isinstance(app_ids, list):
            raise ValueError("Expected app_ids to be of type list")

        app_ids = map(int, app_ids)

        message = MsgProto(EMsg.ClientGamesPlayed)
        GamePlayed = message.body.GamePlayed

        message.body.games_played.extend(map(lambda x: GamePlayed(game_id=x), app_ids))

        self.send(message)
