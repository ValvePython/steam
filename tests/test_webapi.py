import unittest
import mock
import vcr

from steam.webapi import WebAPI
from steam.enums import EType, EUniverse

test_api_key = 'test_api_key'

test_vcr = vcr.VCR(
    record_mode='new_episodes',
    serializer='yaml',
    filter_query_parameters=['key'],
    filter_post_data_parameters=['key'],
    cassette_library_dir='vcr',
)

class TCwebapi(unittest.TestCase):
    @test_vcr.use_cassette('webapi.yaml')
    def setUp(self):
        self.api = WebAPI(test_api_key)
        self.api.session.headers['Accept-Encoding'] = 'identity'

    def test_docs(self):
        self.assertTrue(len(self.api.doc()) > 0)

    @test_vcr.use_cassette('webapi.yaml')
    def test_simple_api_call(self):
        resp = self.api.ISteamWebAPIUtil.GetServerInfo()
        self.assertTrue('servertime' in resp)

    @test_vcr.use_cassette('webapi.yaml')
    def test_simple_api_call_vdf(self):
        resp = self.api.ISteamWebAPIUtil.GetServerInfo(format='vdf')
        self.assertTrue('servertime' in resp['response'])

    @test_vcr.use_cassette('webapi.yaml')
    def test_resolve_vanity(self):
        resp = self.api.ISteamUser.ResolveVanityURL(vanityurl='valve', url_type=2)
        self.assertEqual(resp['response']['steamid'], '103582791429521412')

    @test_vcr.use_cassette('webapi.yaml')
    def test_post_publishedfile(self):
        resp = self.api.ISteamRemoteStorage.GetPublishedFileDetails(itemcount=5, publishedfileids=[1,1,1,1,1])
        self.assertEqual(resp['response']['resultcount'], 5)

        resp = self.api.ISteamUser.ResolveVanityURL(vanityurl='valve', url_type=2)
        self.assertEqual(resp['response']['steamid'], '103582791429521412')
