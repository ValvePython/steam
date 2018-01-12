wallet_steamclient.py
---------------------

Prompts for login, handles code prompts and prints wallet balance.
Since there is no handling for the result of ``cli_login()`` there
might situations where it breaks like when Steam is down.

wallet_webauth.py
-----------------

This script is a little bit more complicated. It logins into the Steam website instead.
Once logged in, it requests a single page and finds the balance in the source code.
There is a basic structure to handle code prompts.
Entering username, password or codes wrong will result in an error as there is no logic to handle that.
