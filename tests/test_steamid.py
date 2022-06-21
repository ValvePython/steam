import unittest
import mock
import vcr

import requests
from steam import steamid
from steam.steamid import SteamID, ETypeChar
from steam.enums import EType, EUniverse, EInstanceFlag

def create_steam64(accountid, etype, euniverse, instance):
    return (euniverse << 56) | (etype << 52) | (instance << 32) | accountid


class SteamID_initialization(unittest.TestCase):
    def compare(self, obj, test_list):
        self.assertEqual(obj.id, test_list[0])
        self.assertEqual(obj.type, test_list[1])
        self.assertEqual(obj.universe, test_list[2])
        self.assertEqual(obj.instance, test_list[3])

    def test_hash(self):
        self.assertEqual(hash(SteamID(1)), hash(SteamID(1)))
        self.assertNotEqual(hash(SteamID(12345)), hash(SteamID(8888)))

    def test_is_valid(self):
        self.assertTrue(SteamID(1).is_valid())
        self.assertTrue(SteamID(id=5).is_valid())

        self.assertFalse(SteamID(0).is_valid())
        self.assertFalse(SteamID(-50).is_valid())

        self.assertFalse(SteamID(id=1, type=EType.Invalid).is_valid())
        self.assertFalse(SteamID(id=1, universe=EUniverse.Invalid).is_valid())

    def test_arg_toomany_invalid(self):
        with self.assertRaises(TypeError):
            SteamID(1,2,3,4,5)
        with self.assertRaises(TypeError):
            SteamID(1,2,3,4,5,6)

    def test_args_only(self):
        self.compare(SteamID(1, 2),
                     [1, 2, 0, 0])
        self.compare(SteamID(1, 2, 3),
                     [1, 2, 3, 0])
        self.compare(SteamID(1, 2, 3, 4),
                     [1, 2, 3, 4])

    ######################################################
    # 1 ARG
    ######################################################
    def test_arg_steam32(self):
        self.compare(SteamID(1),
                     [1, EType.Individual, EUniverse.Public, 1])
        self.compare(SteamID('1'),
                     [1, EType.Individual, EUniverse.Public, 1])
        self.compare(SteamID(12),
                     [12, EType.Individual, EUniverse.Public, 1])
        self.compare(SteamID('12'),
                     [12, EType.Individual, EUniverse.Public, 1])
        self.compare(SteamID(123),
                     [123, EType.Individual, EUniverse.Public, 1])
        self.compare(SteamID('123'),
                     [123, EType.Individual, EUniverse.Public, 1])
        self.compare(SteamID(12345678),
                     [12345678, EType.Individual, EUniverse.Public, 1])
        self.compare(SteamID('12345678'),
                     [12345678, EType.Individual, EUniverse.Public, 1])
        self.compare(SteamID(0xffffFFFF),
                     [0xffffFFFF, EType.Individual, EUniverse.Public, 1])
        self.compare(SteamID(str(0xffffFFFF)),
                     [0xffffFFFF, EType.Individual, EUniverse.Public, 1])

    def test_arg_steam64(self):
        self.compare(SteamID(76580280500085312),
                     [123456, EType.Individual, EUniverse.Public, 4444]
                     )
        self.compare(SteamID('76580280500085312'),
                     [123456, EType.Individual, EUniverse.Public, 4444]
                     )
        self.compare(SteamID(103582791429521412),
                     [4, EType.Clan, EUniverse.Public, 0]
                     )
        self.compare(SteamID('103582791429521412'),
                     [4, EType.Clan, EUniverse.Public, 0]
                     )

    def test_arg_steam64_invalid_universe(self):
        with self.assertRaises(ValueError):
            SteamID(create_steam64(1, 1, 255, 1))

    def test_arg_steam64_invalid_type(self):
        with self.assertRaises(ValueError):
            SteamID(create_steam64(1, 15, 1, 1))

    ######################################################
    # 1 arg - steam2/steam3 format
    ######################################################
    @mock.patch.multiple('steam.steamid',
                         steam2_to_tuple=mock.DEFAULT,
                         steam3_to_tuple=mock.DEFAULT,
                         )
    def test_arg_steam2(self, steam2_to_tuple, steam3_to_tuple):
        steam2_to_tuple.return_value = (1, 2, 3, 4)
        steam3_to_tuple.return_value = (5, 6, 7, 8)

        test_instance = SteamID('STEAM_1:1:1')

        steam2_to_tuple.assert_called_once_with('STEAM_1:1:1')
        self.assertFalse(steam3_to_tuple.called)

        self.compare(test_instance,
                     [1, 2, 3, 4])

    @mock.patch.multiple('steam.steamid',
                         steam2_to_tuple=mock.DEFAULT,
                         steam3_to_tuple=mock.DEFAULT,
                         )
    def test_arg_steam3(self, steam2_to_tuple, steam3_to_tuple):
        steam2_to_tuple.return_value = None
        steam3_to_tuple.return_value = (4, 3, 2, 1)

        test_instance = SteamID('[g:1:4]')

        steam2_to_tuple.assert_called_once_with('[g:1:4]')
        steam3_to_tuple.assert_called_once_with('[g:1:4]')

        self.compare(test_instance,
                     [4, 3, 2, 1])

    def test_arg_text_invalid(self):
        self.compare(SteamID("invalid_format"),
                     [0, EType.Invalid, EUniverse.Invalid, 0])

    def test_arg_too_large_invalid(self):
        self.compare(SteamID(111111111111111111111111111111111111111),
                     [0, EType.Invalid, EUniverse.Invalid, 0])
        self.compare(SteamID("1111111111111111111111111111111111111"),
                     [0, EType.Invalid, EUniverse.Invalid, 0])

    ######################################################
    # KWARGS
    ######################################################
    def test_kwarg_id(self):
        self.assertEqual(SteamID(id=555).id, 555)
        self.assertEqual(SteamID(id='555').id, 555)

    def test_kwarg_type(self):
        with self.assertRaises(KeyError):
            SteamID(id=5, type="doesn't exist")
        with self.assertRaises(ValueError):
            SteamID(id=5, type=99999999)
        with self.assertRaises(KeyError):
            SteamID(id=5, type=None)

        self.assertEqual(SteamID(id=5, type=1).type, EType.Individual)
        self.assertEqual(SteamID(id=5, type='Individual').type, EType.Individual)
        self.assertEqual(SteamID(id=5, type='AnonUser').type, EType.AnonUser)

    def test_kwarg_universe(self):
        with self.assertRaises(KeyError):
            SteamID(id=5, universe="doesn't exist")
        with self.assertRaises(ValueError):
            SteamID(id=5, universe=99999999)
        with self.assertRaises(KeyError):
            SteamID(id=5, universe=None)

        self.assertEqual(SteamID(id=5, universe=1).universe, EUniverse.Public)
        self.assertEqual(SteamID(id=5, universe='Public').universe, EUniverse.Public)
        self.assertEqual(SteamID(id=5, universe='Dev').universe, EUniverse.Dev)

    def test_kwarg_instance(self):
        self.assertEqual(SteamID(id=5, instance=1234).instance, 1234)

        for etype in EType:
            self.assertEqual(SteamID(id=5, type=etype).instance,
                             1 if etype in (EType.Individual, EType.GameServer) else 0)

    def test_kwargs_invalid(self):
        invalid = [0, EType.Invalid, EUniverse.Invalid, 0]

        self.compare(SteamID(), invalid)
        self.compare(SteamID(id=0, type=0, universe=0, instance=0), invalid)
        self.compare(SteamID(id=0,
                             type=EType.Invalid,
                             universe=EUniverse.Invalid,
                             instance=0,
                             ), invalid)
        self.compare(SteamID(id=0,
                             type='Invalid',
                             universe='Invalid',
                             instance=0,
                             ), invalid)


class SteamID_properties(unittest.TestCase):
    def test_repr(self):
        # just to cover in coverage
        self.assertTrue('SteamID' in repr(SteamID()))

    def test_is_valid(self):
        # default
        self.assertFalse(SteamID().is_valid())
        # id = 0
        self.assertFalse(SteamID(0).is_valid())
        self.assertFalse(SteamID(id=0).is_valid())
        self.assertFalse(SteamID(-50).is_valid())
        self.assertFalse(SteamID(id=-50).is_valid())
        # id > 0
        self.assertTrue(SteamID(5).is_valid())
        # type out of bound
        self.assertFalse(SteamID(1, EType.Max).is_valid())
        # universe out of bound
        self.assertFalse(SteamID(1, universe=EUniverse.Max).is_valid())
        # individual
        self.assertTrue(SteamID(123, EType.Individual, EUniverse.Public, instance=0).is_valid())
        self.assertTrue(SteamID(123, EType.Individual, EUniverse.Public, instance=1).is_valid())
        self.assertTrue(SteamID(123, EType.Individual, EUniverse.Public, instance=2).is_valid())
        self.assertTrue(SteamID(123, EType.Individual, EUniverse.Public, instance=3).is_valid())
        self.assertTrue(SteamID(123, EType.Individual, EUniverse.Public, instance=4).is_valid())
        self.assertFalse(SteamID(123, EType.Individual, EUniverse.Public, instance=5).is_valid())
        self.assertFalse(SteamID(123, EType.Individual, EUniverse.Public, instance=333).is_valid())
        # clan
        self.assertTrue(SteamID(1, EType.Clan, EUniverse.Public, instance=0).is_valid())
        self.assertFalse(SteamID(1, EType.Clan, EUniverse.Public, instance=1).is_valid())
        self.assertFalse(SteamID(1, EType.Clan, EUniverse.Public, instance=1234).is_valid())

        s = SteamID(123, type=EType.Clan, universe=EUniverse.Public, instance=333)
        self.assertFalse(s.is_valid())

    def test_rich_comperison(self):
        for test_value in [SteamID(5), 5]:
            self.assertFalse(SteamID(10) == test_value)
            self.assertTrue(SteamID(10) != test_value)
            self.assertTrue(SteamID(10) > test_value)
            self.assertTrue(SteamID(10) >= test_value)
            self.assertFalse(SteamID(10) < test_value)
            self.assertFalse(SteamID(10) <= test_value)

    def test_str(self):
        self.assertEqual(str(SteamID(76580280500085312)), '76580280500085312')

    def test_as_steam2(self):
        self.assertEqual(SteamID('STEAM_0:1:4').as_steam2, 'STEAM_1:1:4')
        self.assertEqual(SteamID('STEAM_1:1:4').as_steam2, 'STEAM_1:1:4')
        self.assertEqual(SteamID('STEAM_0:0:4').as_steam2, 'STEAM_1:0:4')
        self.assertEqual(SteamID('STEAM_1:0:4').as_steam2, 'STEAM_1:0:4')

        self.assertEqual(SteamID('STEAM_4:0:4').as_steam2, 'STEAM_4:0:4')
        self.assertEqual(SteamID('STEAM_4:1:4').as_steam2, 'STEAM_4:1:4')

    def test_as_steam2_zero(self):
        self.assertEqual(SteamID('STEAM_0:1:4').as_steam2_zero, 'STEAM_0:1:4')
        self.assertEqual(SteamID('STEAM_1:1:4').as_steam2_zero, 'STEAM_0:1:4')
        self.assertEqual(SteamID('STEAM_0:0:4').as_steam2_zero, 'STEAM_0:0:4')
        self.assertEqual(SteamID('STEAM_1:0:4').as_steam2_zero, 'STEAM_0:0:4')

        self.assertEqual(SteamID('STEAM_4:0:4').as_steam2_zero, 'STEAM_4:0:4')
        self.assertEqual(SteamID('STEAM_4:1:4').as_steam2_zero, 'STEAM_4:1:4')

    def test_as_steam3(self):
        self.assertEqual(SteamID('[U:1:1234]').as_steam3, '[U:1:1234]')
        self.assertEqual(SteamID('[U:1:1234:56]').as_steam3, '[U:1:1234:56]')
        self.assertEqual(SteamID('[g:1:4]').as_steam3, '[g:1:4]')
        self.assertEqual(SteamID('[A:1:1234:567]').as_steam3, '[A:1:1234:567]')
        self.assertEqual(SteamID('[G:1:1234:567]').as_steam3, '[G:1:1234]')
        self.assertEqual(SteamID('[T:1:1234]').as_steam3, '[T:1:1234]')
        self.assertEqual(SteamID('[c:1:1234]').as_steam3, '[c:1:1234]')
        self.assertEqual(SteamID('[L:1:1234]').as_steam3, '[L:1:1234]')

    def test_as_32(self):
        self.assertEqual(SteamID(76580280500085312).as_32, 123456)

    def test_as_64(self):
        self.assertEqual(SteamID(76580280500085312).as_64, 76580280500085312)

    def test_community_url(self):
        # user url
        self.assertEqual(SteamID(76580280500085312).community_url,
                         'https://steamcommunity.com/profiles/76580280500085312'
                         )
        # group url
        self.assertEqual(SteamID('[g:1:4]').community_url,
                         'https://steamcommunity.com/gid/103582791429521412'
                         )
        # else None
        self.assertEqual(SteamID('[A:1:4]').community_url,
                         None
                         )

    def test_as_invite_code(self):
        self.assertEqual(SteamID(0         , EType.Individual, EUniverse.Public, instance=1).as_invite_code, None)
        self.assertEqual(SteamID(1         , EType.Invalid   , EUniverse.Public, instance=1).as_invite_code, None)
        self.assertEqual(SteamID(1         , EType.Clan      , EUniverse.Public, instance=1).as_invite_code, None)
        self.assertEqual(SteamID(1         , EType.Individual, EUniverse.Beta  , instance=1).as_invite_code, 'c')
        self.assertEqual(SteamID(1         , EType.Individual, EUniverse.Public, instance=1).as_invite_code, 'c')
        self.assertEqual(SteamID(123456    , EType.Individual, EUniverse.Public, instance=1).as_invite_code, 'cv-dgb')
        self.assertEqual(SteamID(4294967295, EType.Individual, EUniverse.Public, instance=1).as_invite_code, 'wwww-wwww')

    def test_as_csgo_friend_code(self):
        self.assertEqual(SteamID(0         , EType.Individual, EUniverse.Public, instance=1).as_csgo_friend_code, None)
        self.assertEqual(SteamID(1         , EType.Invalid   , EUniverse.Public, instance=1).as_csgo_friend_code, None)
        self.assertEqual(SteamID(1         , EType.Clan      , EUniverse.Public, instance=1).as_csgo_friend_code, None)
        self.assertEqual(SteamID(1         , EType.Individual, EUniverse.Beta  , instance=1).as_csgo_friend_code, 'AJJJS-ABAA')
        self.assertEqual(SteamID(1         , EType.Individual, EUniverse.Public, instance=1).as_csgo_friend_code, 'AJJJS-ABAA')
        self.assertEqual(SteamID(123456    , EType.Individual, EUniverse.Public, instance=1).as_csgo_friend_code, 'ABNBT-GBDC')
        self.assertEqual(SteamID(4294967295, EType.Individual, EUniverse.Public, instance=1).as_csgo_friend_code, 'S9ZZR-999P')

    def test_as_invite_url(self):
        self.assertEqual(SteamID(0     , EType.Individual, EUniverse.Public, instance=1).invite_url, None)
        self.assertEqual(SteamID(123456, EType.Individual, EUniverse.Public, instance=1).invite_url, 'https://s.team/p/cv-dgb')
        self.assertEqual(SteamID(123456, EType.Individual, EUniverse.Beta  , instance=1).invite_url, 'https://s.team/p/cv-dgb')
        self.assertEqual(SteamID(123456, EType.Invalid   , EUniverse.Public, instance=1).invite_url, None)
        self.assertEqual(SteamID(123456, EType.Clan      , EUniverse.Public, instance=1).invite_url, None)


class steamid_functions(unittest.TestCase):
    @mock.patch('steam.steamid.steam64_from_url')
    def test_from_url(self, s64_from_url):

        s64_from_url.return_value = None
        self.assertIsNone(steamid.from_url(None))

        s64_from_url.return_value = '76580280500085312'
        test_instance = steamid.from_url('76580280500085312')
        self.assertIsInstance(test_instance, SteamID)
        self.assertEqual(test_instance.as_64, 76580280500085312)

    @mock.patch('steam.steamid.make_requests_session')
    def test_steam64_from_url_timeout(self, mrs_mock):
        mm = mrs_mock.return_value = mock.MagicMock()

        mm.get.side_effect = requests.exceptions.ConnectTimeout('test')
        self.assertIsNone(steamid.steam64_from_url("https://steamcommunity.com/id/timeout_me"))

        mm.get.reset_mock()
        mm.get.side_effect = requests.exceptions.ReadTimeout('test')
        self.assertIsNone(steamid.steam64_from_url("https://steamcommunity.com/id/timeout_me"))

    def test_steam64_from_url(self):
        def scrub_req(r):
            r.headers.pop('Cookie', None)
            r.headers.pop('Date', None)
            return r
        def scrub_resp(r):
            r['headers'].pop('Set-Cookie', None)
            r['headers'].pop('Date', None)
            return r

        with vcr.use_cassette('vcr/steamid_community_urls.yaml',
                              mode='once',
                              serializer='yaml',
                              filter_query_parameters=['nocache'],
                              decode_compressed_response=False,
                              before_record_request=scrub_req,
                              before_record_response=scrub_resp,
                              ):
            # invalid urls return None
            self.assertIsNone(steamid.steam64_from_url("asdasd"))
            self.assertIsNone(steamid.steam64_from_url("https://steamcommunity.com/gid/0"))

            # try profile urls
            sid = steamid.steam64_from_url('https://steamcommunity.com/profiles/[U:1:12]')
            self.assertEqual(sid, 76561197960265740)

            sid = steamid.steam64_from_url('https://steamcommunity.com/profiles/76561197960265740')
            self.assertEqual(sid, 76561197960265740)

            sid = steamid.steam64_from_url('https://steamcommunity.com/id/johnc')
            self.assertEqual(sid, 76561197960265740)

            sid = steamid.steam64_from_url('https://steamcommunity.com/user/r')
            self.assertEqual(sid, 76561197960265740)

            # try group urls
            sid = steamid.steam64_from_url('https://steamcommunity.com/gid/[g:1:4]')
            self.assertEqual(sid, 103582791429521412)

            sid = steamid.steam64_from_url('https://steamcommunity.com/gid/103582791429521412')
            self.assertEqual(sid, 103582791429521412)

            sid = steamid.steam64_from_url('https://steamcommunity.com/groups/Valve')
            self.assertEqual(sid, 103582791429521412)

    def test_arg_steam2(self):
        self.assertIsNone(steamid.steam2_to_tuple('invalid_format'))

        self.assertEqual(steamid.steam2_to_tuple("STEAM_0:1:1"),
                         (3, EType.Individual, EUniverse.Public, 1)
                         )
        self.assertEqual(steamid.steam2_to_tuple("STEAM_1:1:1"),
                         (3, EType.Individual, EUniverse.Public, 1)
                         )
        self.assertEqual(steamid.steam2_to_tuple("STEAM_0:0:4"),
                         (8, EType.Individual, EUniverse.Public, 1)
                         )
        self.assertEqual(steamid.steam2_to_tuple("STEAM_1:0:4"),
                         (8, EType.Individual, EUniverse.Public, 1)
                         )
        self.assertEqual(steamid.steam2_to_tuple("STEAM_4:1:1"),
                         (3, EType.Individual, EUniverse.Dev, 1)
                         )
        self.assertEqual(steamid.steam2_to_tuple("STEAM_4:0:4"),
                         (8, EType.Individual, EUniverse.Dev, 1)
                         )

    def test_arg_steam3(self):
        self.assertIsNone(steamid.steam3_to_tuple('invalid_format'))
        self.assertIsNone(steamid.steam3_to_tuple(''))
        self.assertIsNone(steamid.steam3_to_tuple(' '))
        self.assertIsNone(steamid.steam3_to_tuple('[U:5:1234]'))
        self.assertIsNone(steamid.steam3_to_tuple('[i:5:1234]'))

        self.assertEqual(steamid.steam3_to_tuple("[i:1:1234]"),
                         (1234, EType.Invalid, EUniverse.Public, 0)
                         )
        self.assertEqual(steamid.steam3_to_tuple("[I:1:1234]"),
                         (1234, EType.Invalid, EUniverse.Public, 0)
                         )
        self.assertEqual(steamid.steam3_to_tuple("[U:0:1234]"),
                         (1234, EType.Individual, EUniverse.Invalid, 1)
                         )

        self.assertEqual(steamid.steam3_to_tuple("[U:1:1234]"),
                         (1234, EType.Individual, EUniverse.Public, 1)
                         )
        self.assertEqual(steamid.steam3_to_tuple("[G:1:1234]"),
                         (1234, EType.GameServer, EUniverse.Public, 1)
                         )
        self.assertEqual(steamid.steam3_to_tuple("[g:1:4]"),
                         (4, EType.Clan, EUniverse.Public, 0)
                         )
        self.assertEqual(steamid.steam3_to_tuple("[A:1:4]"),
                         (4, EType.AnonGameServer, EUniverse.Public, 0)
                         )
        self.assertEqual(steamid.steam3_to_tuple("[A:1:1234:567]"),
                         (1234, EType.AnonGameServer, EUniverse.Public, 567)
                         )
        self.assertEqual(steamid.steam3_to_tuple("[T:1:1234]"),
                         (1234, EType.Chat, EUniverse.Public, 0)
                         )
        self.assertEqual(steamid.steam3_to_tuple("[L:1:1234]"),
                         (1234, EType.Chat, EUniverse.Public, EInstanceFlag.Lobby)
                         )
        self.assertEqual(steamid.steam3_to_tuple("[c:1:1234]"),
                         (1234, EType.Chat, EUniverse.Public, EInstanceFlag.Clan)
                         )

    def test_from_invite_code(self):
        self.assertIsNone(steamid.from_invite_code('invalid_format'))
        self.assertIsNone(steamid.from_invite_code('https://steamcommunity.com/p/cv-dgb'))
        self.assertIsNone(steamid.from_invite_code('b'))
        self.assertIsNone(steamid.from_invite_code('aaaaaaaaaaaaaaaaaaaaaaaaa'))

        self.assertEqual(steamid.from_invite_code('c', EUniverse.Beta),
                         SteamID(1, EType.Individual, EUniverse.Beta, 1))
        self.assertEqual(steamid.from_invite_code('c'),
                         SteamID(1, EType.Individual, EUniverse.Public, 1))
        self.assertEqual(steamid.from_invite_code('http://s.team/p/c', EUniverse.Beta),
                         SteamID(1, EType.Individual, EUniverse.Beta, 1))
        self.assertEqual(steamid.from_invite_code('http://s.team/p/c'),
                         SteamID(1, EType.Individual, EUniverse.Public, 1))
        self.assertEqual(steamid.from_invite_code('https://s.team/p/cv-dgb'),
                         SteamID(123456, EType.Individual, EUniverse.Public, 1))
        self.assertEqual(steamid.from_invite_code('https://s.team/p/cv-dgb/ABCDE12354'),
                         SteamID(123456, EType.Individual, EUniverse.Public, 1))
        self.assertEqual(steamid.from_invite_code('http://s.team/p/wwww-wwww'),
                         SteamID(4294967295, EType.Individual, EUniverse.Public, 1))

    def test_from_csgo_friend_code(self):
        self.assertIsNone(steamid.from_csgo_friend_code(''))
        self.assertIsNone(steamid.from_csgo_friend_code('aaaaaaaaaaaaaaaaaaaaaaaaaaaa'))
        self.assertIsNone(steamid.from_csgo_friend_code('11111-1111'))

        self.assertEqual(steamid.from_csgo_friend_code('AJJJS-ABAA', EUniverse.Beta),
                         SteamID(1, EType.Individual, EUniverse.Beta, instance=1))
        self.assertEqual(steamid.from_csgo_friend_code('AJJJS-ABAA'),
                         SteamID(1, EType.Individual, EUniverse.Public, instance=1))
        self.assertEqual(steamid.from_csgo_friend_code('ABNBT-GBDC'),
                         SteamID(123456, EType.Individual, EUniverse.Public, instance=1))
        self.assertEqual(steamid.from_csgo_friend_code('S9ZZR-999P'),
                         SteamID(4294967295, EType.Individual, EUniverse.Public, instance=1))
