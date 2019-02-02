# https://github.com/ValvePython/steam/issues/97
import gevent.monkey
gevent.monkey.patch_all()

from getpass import getpass
from gevent.pywsgi import WSGIServer
from steam_worker import SteamWorker
from flask import Flask, request, abort, jsonify

import logging
logging.basicConfig(format="%(asctime)s | %(name)s | %(message)s", level=logging.INFO)
LOG = logging.getLogger('SimpleWebAPI')

app = Flask('SimpleWebAPI')

@app.route("/ISteamApps/GetProductInfo/", methods=['GET'])
def GetProductInfo():
    appids = request.args.get('appids', '')
    pkgids = request.args.get('packageids', '')

    if not appids and not pkgids:
        return jsonify({})

    appids = map(int, appids.split(',')) if appids else []
    pkgids = map(int, pkgids.split(',')) if pkgids else []

    return jsonify(worker.get_product_info(appids, pkgids) or {})

@app.route("/ISteamApps/GetProductChanges/", methods=['GET'])
def GetProductChanges():
    chgnum = int(request.args.get('since_changenumber', 0))
    return jsonify(worker.get_product_changes(chgnum))

@app.route("/ISteamApps/GetPlayerCount/", methods=['GET'])
def GetPlayerCount():
    appid = int(request.args.get('appid', 0))
    return jsonify(worker.get_player_count(appid))


if __name__ == "__main__":
    LOG.info("Simple Web API recipe")
    LOG.info("-"*30)
    LOG.info("Starting Steam worker...")

    worker = SteamWorker()
    worker.prompt_login()

    LOG.info("Starting HTTP server...")
    http_server = WSGIServer(('', 5000), app)

    try:
        http_server.serve_forever()
    except KeyboardInterrupt:
        LOG.info("Exit requested")
        worker.close()
