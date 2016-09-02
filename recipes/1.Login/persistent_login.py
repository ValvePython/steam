from __future__ import handle_function
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

@client.on("connected")
def handle_connected():
    LOG.info("Connected to %s", client.current_server_addr)

@client.on("reconnect")
def handle_reconnect(delay):
    LOG.info("Reconnect in %ds...", delay)

@client.on("disconnected")
def handle_disconnect():
    LOG.info("Disconnected.")

    try:
        client.wait_event("auth_code_required", timeout=2, raises=True)
    except:
        LOG.info("Reconnecting...")
        client.reconnect(maxdelay=30)

@client.on("auth_code_required")
def auth_code_prompt(is_2fa, mismatch):
    if mismatch:
        LOG.info("Previous code was incorrect")

    if is_2fa:
        code = raw_input("Enter 2FA Code: ")
        client.login(two_factor_code=code, **logon_details)
    else:
        code = raw_input("Enter Email Code: ")
        client.login(auth_code=code, **logon_details)

@client.on("logged_on")
def handle_after_logon():
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
        LOG.info("Logout")
        client.logout()
