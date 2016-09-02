from __future__ import print_function
from getpass import getpass
import gevent
from steam import SteamClient


print("One-off login recipe")
print("-"*20)

logon_details = {
    'username': raw_input("Steam user: "),
    'password': getpass("Password: "),
}


client = SteamClient()

@client.on('error')
def error(result):
    print("Logon result:", repr(result))

@client.on('auth_code_required')
def auth_code_prompt(is_2fa, mismatch):
    if is_2fa:
        code = raw_input("Enter 2FA Code: ")
        client.login(two_factor_code=code, **logon_details)
    else:
        code = raw_input("Enter Email Code: ")
        client.login(auth_code=code, **logon_details)

print("-"*20)

client.login(**logon_details)

try:
    client.wait_event('logged_on')
except:
    raise SystemExit

print("-"*20)
print("Logged on as:", client.user.name)
print("Community profile:", client.steam_id.community_url)
print("Last logon:", client.user.last_logon)
print("Last logoff:", client.user.last_logoff)

gevent.idle()
client.logout()
