import mock
from steam import webapi
import unittest


class TestWebAPI(unittest.TestCase):
    @mock.patch('steam.webapi.WebAPI._api_request', mock.Mock())
    @mock.patch('steam.webapi.WebAPI.load_interfaces', mock.Mock())
    def test_with_key(self):
        api = webapi.WebAPI(key='testkey')
        api.ISteamUser = webapi.WebAPIInterface({
            'name': 'ISteamUser',
            'methods': [
                {
                    "name": "GetPlayerSummaries",
                    "version": 2,
                    "httpmethod": "GET",
                    "parameters": [
                        {
                            "name": "key",
                            "type": "string",
                            "optional": False,
                            "description": "access key"
                        },
                        {
                            "name": "steamids",
                            "type": "string",
                            "optional": False,
                            "description": "Comma-delimited list of SteamIDs (max: 100)"
                        }
                    ]

                },

            ]
        }, parent=api)
        api.ISteamUser.GetPlayerSummaries(steamids='76561197960435530')
