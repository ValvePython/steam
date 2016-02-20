import os
import logging
import gevent
from Crypto.Hash import SHA
from eventemitter import EventEmitter
from steam.enums.emsg import EMsg
from steam.enums import EResult, EOSType
from steam.core.msg import MsgProto
from steam.core.cm import CMClient
from steam import SteamID
from steam.client.features import FeatureBase

logger = logging.getLogger("SteamClient")


class SteamClient(EventEmitter, FeatureBase):
    current_jobid = 0
    credential_location = None
    username = None

    def __init__(self):
        self.cm = CMClient()

        # register listners
        self.cm.on(None, self._handle_cm_events)
        self.on(EMsg.ClientLogOnResponse, self._handle_logon)
        self.on(EMsg.ClientUpdateMachineAuth, self._handle_update_machine_auth)
        self.on("disconnected", self._handle_disconnect)

        self.logged_on = False

        super(SteamClient, self).__init__()

    def __repr__(self):
        return "<%s() %s>" % (self.__class__.__name__,
                              'online' if self.connected else 'offline',
                              )

    def emit(self, event, *args):
        if event is not None:
            logger.debug("Emit event: %s" % repr(event))
        super(SteamClient, self).emit(event, *args)

    def set_credential_location(self, path):
        self.credential_location = path

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

    def _handle_cm_events(self, event, *args):
        self.emit(event, *args)

        if isinstance(event, EMsg):
            message = args[0]

            if message.proto:
                jobid = message.header.jobid_target
            else:
                jobid = message.header.targetJobID

            if jobid not in (-1, 18446744073709551615):
                self.emit("job_%d" % jobid, *args)

    def _handle_disconnect(self):
        self.username = None
        self.logged_on = False
        self.current_jobid = 0

    def _handle_logon(self, msg):
        result = EResult(msg.body.eresult)

        if result == EResult.OK:
            self.logged_on = True
            self.emit("logged_on")
            return

        # CM kills the connection on error anyway
        self.disconnect()

        if result in (EResult.AccountLogonDenied,
                      EResult.InvalidLoginAuthCode,
                      EResult.AccountLoginDeniedNeedTwoFactor,
                      EResult.TwoFactorCodeMismatch,
                      ):

            is_2fa = (result in (EResult.AccountLoginDeniedNeedTwoFactor,
                                 EResult.TwoFactorCodeMismatch,
                                 ))

            if is_2fa:
                code_mismatch = (result == EResult.TwoFactorCodeMismatch)
            else:
                code_mismatch = (result == EResult.InvalidLoginAuthCode)

            self.emit("auth_code_required", is_2fa, code_mismatch)
        else:
            self.emit("error", result)

    def _handle_update_machine_auth(self, message):
        ok = self.store_sentry(self.username, message.body.bytes)

        if ok:
            resp = MsgProto(EMsg.ClientUpdateMachineAuthResponse)

            resp.header.jobid_target = message.header.jobid_source

            resp.body.filename = message.body.filename
            resp.body.eresult = EResult.OK
            resp.body.sha_file = SHA.new(message.body.bytes).digest()
            resp.body.getlasterror = 0
            resp.body.offset = message.body.offset
            resp.body.cubwrote = message.body.cubtowrite

            self.send(resp)

    def send(self, message):
        if not self.connected:
            raise RuntimeError("Cannot send message while not connected")

        self.cm.send_message(message)

    def send_job(self, message):
        jobid = self.current_jobid = (self.current_jobid + 1) % 4294967295

        if message.proto:
            message.header.jobid_source = jobid
        else:
            message.header.sourceJobID = jobid

        self.send(message)

        return "job_%d" % jobid

    def _pre_login(self):
        if self.logged_on:
            logger.debug("Trying to login while logged on???")
            raise RuntimeError("Already logged on")

        if not self.connected:
            self.connect()

        if not self.cm.channel_secured:
            self.wait_event("channel_secured")

    def _get_sentry_path(self, username):
        if self.credential_location is not None:
            return os.path.join(self.credential_location,
                                "%s_sentry.bin" % username
                                 )
        return None

    def get_sentry(self, username):
        filepath = self._get_sentry_path(username)

        if filepath and os.path.isfile(filepath):
            try:
                with open(filepath, 'r') as f:
                    return f.read()
            except IOError as e:
                logger.error("get_sentry: %s" % str(e))

        return None

    def store_sentry(self, username, sentry_bytes):
        filepath = self._get_sentry_path(username)
        if filepath:
            try:
                with open(filepath, 'w') as f:
                    f.write(sentry_bytes)
                return True
            except IOError as e:
                logger.error("store_sentry: %s" % str(e))

        return False

    def login(self, username, password, auth_code=None, two_factor_code=None, remember=False):
        logger.debug("Attempting login")

        self._pre_login()

        self.username = username

        message = MsgProto(EMsg.ClientLogon)
        message.header.steamid = SteamID(type='Individual', universe='Public')
        message.body.protocol_version = 65575
        message.body.client_package_version = 1771
        message.body.client_os_type = EOSType.Win10
        message.body.client_language = "english"

        message.body.account_name = username
        message.body.password = password

        sentry = self.get_sentry(username)
        if sentry is None:
            message.body.eresult_sentryfile = EResult.FileNotFound
        else:
            message.body.eresult_sentryfile = EResult.OK
            message.body.sha_sentryfile = SHA.new(sentry).digest()

        if auth_code:
            message.body.auth_code = auth_code
        if two_factor_code:
            message.body.two_factor_code = two_factor_code

        self.send(message)

    def anonymous_login(self):
        logger.debug("Attempting Anonymous login")

        self._pre_login()

        message = MsgProto(EMsg.ClientLogon)
        message.header.steamid = SteamID(type='AnonUser', universe='Public')
        message.body.protocol_version = 65575
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
