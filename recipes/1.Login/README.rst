one_off_login.py
----------------

Minimal example for login, support email and two factor codes.
After the login, the code will print some account info and exit.
No information is persisted to disk.

persistent_login.py
-------------------

In this example, after the login prompt, the client will remain connected until interrupted.
The client will attempt to reconnect after losing network connectivity or when steam is down.

