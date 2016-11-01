import logging
import gevent
from getpass import getpass
from steam import SteamClient

logging.basicConfig(format="%(asctime)s | %(message)s", level=logging.INFO)
LOG = logging.getLogger()

LOG.info("Persistent logon recipe")
LOG.info("-"*30)

logon_details = {
    "username": raw_input("Steam user: "),
    "password": getpass("Password: "),
}
logged_on_once = False

client = SteamClient()
client.set_credential_location(".")

@client.on("error")
def handle_error(result):
    LOG.info("Logon result: %s", repr(result))

@client.on("channel_secured")
def send_login():
    if client.relogin_available:
        client.relogin()
    else:
        client.login(**logon_details)
        logon_details.pop('auth_code', None)
        logon_details.pop('two_factor_code', None)

@client.on("connected")
def handle_connected():
    LOG.info("Connected to %s", client.current_server_addr)

@client.on("reconnect")
def handle_reconnect(delay):
    LOG.info("Reconnect in %ds...", delay)

@client.on("disconnected")
def handle_disconnect():
    LOG.info("Disconnected.")

    if logged_on_once:
        LOG.info("Reconnecting...")
        client.reconnect(maxdelay=30)

@client.on("auth_code_required")
def auth_code_prompt(is_2fa, mismatch):
    if mismatch:
        LOG.info("Previous code was incorrect")

    if is_2fa:
        code = raw_input("Enter 2FA Code: ")
        logon_details['two_factor_code'] = code
    else:
        code = raw_input("Enter Email Code: ")
        logon_details['auth_code'] = code

    client.connect()

@client.on("logged_on")
def handle_after_logon():
    global logged_on_once
    logged_on_once = True

    LOG.info("-"*30)
    LOG.info("Logged on as: %s", client.user.name)
    LOG.info("Community profile: %s", client.steam_id.community_url)
    LOG.info("Last logon: %s", client.user.last_logon)
    LOG.info("Last logoff: %s", client.user.last_logoff)
    LOG.info("-"*30)
    LOG.info("Press ^C to exit")


try:
    client.connect()
    client.run_forever()
except KeyboardInterrupt:
    if client.connected:
        logged_on_once = False
        LOG.info("Logout")
        client.logout()
