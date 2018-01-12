from steam.client import SteamClient, EMsg
from steam.enums import EResult, ECurrencyCode

client = SteamClient()

@client.on(EMsg.ClientWalletInfoUpdate)
def print_balance(msg):
    bucks, cents = divmod(msg.body.balance64, 100)
    print("Current balance is {:d}.{:02d} {:s}".format(bucks,
                                                       cents,
                                                       ECurrencyCode(msg.body.currency).name
                                                       ))

client.cli_login()
client.disconnect()
