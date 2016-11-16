one_off_login.py
----------------

Minimal example to login into Steam, print some account info and exit.
No information is persisted to disk.

diy_one_off_login.py
--------------------

Same as above, we make our own prompts instead of using ``cli_login()``

persistent_login.py
-------------------

In this example, after the login prompt, the client will remain connected until interrupted.
The client will attempt to reconnect after losing network connectivity or when steam is down.
A sentry file is persisted to disk for each account.

