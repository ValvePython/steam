Simple Web API recipe
---------------------

Valve doesn't have a Web API for everything, and they don't need to.
We are going to use the ``steam`` and ``flask`` to build a Web API.
First, we need to install ``flask``.

.. code:: bash

    (env)$ pip install flask

``run_webapi.py`` contains our HTTP server app and ``steam_worker.py`` is
a modified version of persistent login recipe that will talk with steam.

Let's run the app:

.. code:: bash

    (env)$ python run_webapi.py
    2016-11-01 00:00:01,000 | SimpleWebAPI | Simple Web API recipe
    2016-11-01 00:00:02,000 | SimpleWebAPI | ------------------------------
    2016-11-01 00:00:03,000 | SimpleWebAPI | Starting Steam worker...
    Username: myusername
    Password:
    2016-11-01 00:00:04,000 | Steam Worker | Connected to (u'1.2.3.4', 27018)
    2016-11-01 00:00:05,000 | SimpleWebAPI | Starting HTTP server...
    2016-11-01 00:00:06,000 | Steam Worker | ------------------------------
    2016-11-01 00:00:07,000 | Steam Worker | Logged on as: FriendlyGhost
    ...
    127.0.0.1 - - [2016-01-01 00:00:08] "GET /ISteamApps/GetPlayerCount/?appid=0 HTTP/1.1" 200 155 0.262596
    ...


Here are the available endpoints:

.. code:: bash

    $ curl -s 127.0.0.1:5000/ISteamApps/GetProductInfo/?appids=570,730 | head -56
    {
      "apps": [
        {
          "appid": 570,
          "appinfo": {
            "appid": "570",
            "common": {
              "clienticon": "c0d15684e6c186289b50dfe083f5c562c57e8fb6",
              "clienttga": "5ca2b133f8fdf56c3d81dd73d1254f95f0614265",
              "community_hub_visible": "1",
              "controllervr": {
                "steamvr": "1"
              },
              "exfgls": "1",
              "gameid": "570",
              "header_image": {
                "english": "header.jpg"
              },
              "icon": "0bbb630d63262dd66d2fdd0f7d37e8661a410075",
              "linuxclienticon": "e1c520b6a98b1fed674a117e9356cdb9ddc6d40c",
              "logo": "d4f836839254be08d8e9dd333ecc9a01782c26d2",
              "logo_small": "d4f836839254be08d8e9dd333ecc9a01782c26d2_thumb",
              "metacritic_fullurl": "http://www.metacritic.com/game/pc/dota-2?ftag=MCD-06-10aaa1f",
              "metacritic_name": "Dota 2",
              "metacritic_score": "90",



    $ curl -s 127.0.0.1:5000/ISteamApps/GetProductChanges/?since_changenumber=2397700 | head -10
    {
      "app_changes": [
        {
          "appid": 730,
          "change_number": 2409212
        },
        {
          "appid": 740,
          "change_number": 2409198
        },



    $ curl 127.0.0.1:5000/ISteamApps/GetPlayerCount/?appid=0
    {
      "eresult": 1,
      "player_count": 2727080
    }
