import unittest
import mock
import vcr

from steam.webapi import WebAPI, requests
from steam.enums import EType, EUniverse

test_api_key = 'test_api_key'


class TCwebapi(unittest.TestCase):
    @vcr.use_cassette('vcr/webapi_init.json', mode='once', serializer='json')
    def test_initialization(self):
        api = WebAPI(test_api_key)
