This are basic examples how to get the wallet balance

wallet_steamclient.py
---------------------

This first script is very basic.
Prompts for loging, handles code prompts and prints wallet balalnce.
Since there is no handling for the result of ``cli_login`` during
this might break in certain situations like when Steam is down.

wallet_webauth.py
-----------------

This script is a little bit more complicated and instead logs in to the steam website.
Once logged in to the website, it requests a single page and finds the balance in the source code.
There is basic structure to handle code prompts.
Entering username, password or codes wrong will result in an error as there is na ologic to handle that.
