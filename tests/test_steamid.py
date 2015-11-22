import unittest
import mock
import vcr

from steam import steamid
from steam.steamid import SteamID
from steam.enums import EType, EUniverse


class SteamID_initialization(unittest.TestCase):
    def compare(self, obj, test_list):
        self.assertEqual(obj.id, test_list[0])
        self.assertEqual(obj.type, test_list[1])
        self.assertEqual(obj.universe, test_list[2])
        self.assertEqual(obj.instance, test_list[3])

    def test_arg_toomany(self):
        with self.assertRaises(ValueError):
            SteamID(1, 2)
        with self.assertRaises(ValueError):
            SteamID(1, 2, 3)
        with self.assertRaises(ValueError):
            SteamID(1, 2, 3, 4)

    ######################################################
    # 1 ARG
    ######################################################
    def test_arg_number_out_of_range(self):
        self.assertRaises(ValueError, SteamID, -1)
        self.assertRaises(ValueError, SteamID, '-1')
        self.assertRaises(ValueError, SteamID, -5555555)
        self.assertRaises(ValueError, SteamID, '-5555555')
        self.assertRaises(ValueError, SteamID, 2**64)
        self.assertRaises(ValueError, SteamID, str(2**64))
        self.assertRaises(ValueError, SteamID, 2**128)
        self.assertRaises(ValueError, SteamID, str(2**128))

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

    ######################################################
    # 1 arg - steam2/steam3 format
    ######################################################
    def test_arg_text_invalid(self):
        with self.assertRaises(ValueError):
            SteamID("randomtext")

    def test_arg_steam2(self):
        self.compare(SteamID("STEAM_0:1:1"),
                     [3, EType.Individual, EUniverse.Public, 1]
                     )
        self.compare(SteamID("STEAM_1:1:1"),
                     [3, EType.Individual, EUniverse.Public, 1]
                     )
        self.compare(SteamID("STEAM_0:0:4"),
                     [8, EType.Individual, EUniverse.Public, 1]
                     )
        self.compare(SteamID("STEAM_1:0:4"),
                     [8, EType.Individual, EUniverse.Public, 1]
                     )

    def test_arg_steam3(self):
        self.compare(SteamID("[U:1:1234]"),
                     [1234, EType.Individual, EUniverse.Public, 1]
                     )
        self.compare(SteamID("[G:1:1234]"),
                     [1234, EType.GameServer, EUniverse.Public, 1]
                     )
        self.compare(SteamID("[g:1:4]"),
                     [4, EType.Clan, EUniverse.Public, 0]
                     )
        self.compare(SteamID("[A:1:4]"),
                     [4, EType.AnonGameServer, EUniverse.Public, 0]
                     )
        self.compare(SteamID("[A:1:1234:567]"),
                     [1234, EType.AnonGameServer, EUniverse.Public, 567]
                     )

    ######################################################
    # KWARGS
    ######################################################
    def test_kwarg_id(self):
        # id kwarg is required always
        with self.assertRaises(ValueError):
            SteamID(instance=0)
            SteamID(id=None)

        self.assertEqual(SteamID(id=555).id, 555)
        self.assertEqual(SteamID(id='555').id, 555)

    def test_kwarg_type(self):
        with self.assertRaises(KeyError):
            SteamID(id=5, type="doesn't exist")
        with self.assertRaises(ValueError):
            SteamID(id=5, type=99999999)
        with self.assertRaises(AttributeError):
            SteamID(id=5, type=None)

        self.assertEqual(SteamID(id=5, type=1).type, EType.Individual)
        self.assertEqual(SteamID(id=5, type='Individual').type, EType.Individual)
        self.assertEqual(SteamID(id=5, type='iNDIVIDUAL').type, EType.Individual)

    def test_kwarg_universe(self):
        with self.assertRaises(KeyError):
            SteamID(id=5, universe="doesn't exist")
        with self.assertRaises(ValueError):
            SteamID(id=5, universe=99999999)
        with self.assertRaises(AttributeError):
            SteamID(id=5, universe=None)

        self.assertEqual(SteamID(id=5, universe=1).universe, EUniverse.Public)
        self.assertEqual(SteamID(id=5, universe='Public').universe, EUniverse.Public)
        self.assertEqual(SteamID(id=5, universe='pUBLIC').universe, EUniverse.Public)

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
        self.compare(SteamID(id=0,
                             type='iNVALID',
                             universe='iNVALID',
                             instance=0,
                             ), invalid)


class SteamID_properties(unittest.TestCase):
    def test_repr(self):
        # just to cover in coverage
        repr(SteamID())

    def test_str(self):
        self.assertEqual(str(SteamID(76580280500085312)), '76580280500085312')

    def test_as_steam2(self):
        self.assertEqual(SteamID('STEAM_0:1:4').as_steam2, 'STEAM_0:1:4')
        self.assertEqual(SteamID('STEAM_1:1:4').as_steam2, 'STEAM_0:1:4')

    def test_as_steam3(self):
        self.assertEqual(SteamID('[U:1:1234]').as_steam3, '[U:1:1234]')
        self.assertEqual(SteamID('[g:1:4]').as_steam3, '[g:1:4]')
        self.assertEqual(SteamID('[A:1:1234:567]').as_steam3, '[A:1:1234:567]')
        self.assertEqual(SteamID('[G:1:1234:567]').as_steam3, '[G:1:1234]')

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


class steamid_functions(unittest.TestCase):
    @mock.patch('steam.steamid.steam64_from_url')
    def test_from_url(self, s64_from_url):

        s64_from_url.return_value = None
        self.assertIsNone(steamid.from_url(None))

        s64_from_url.return_value = '76580280500085312'
        test_instance = steamid.from_url('76580280500085312')
        self.assertIsInstance(test_instance, SteamID)
        self.assertEqual(test_instance.as_64, 76580280500085312)


    @vcr.use_cassette('vcr/steamid_community_urls.yaml', mode='once', serializer='yaml')
    def test_steam64_from_url(self):

        # invalid urls return None
        self.assertIsNone(steamid.steam64_from_url("asdasd"))
        self.assertIsNone(steamid.steam64_from_url("https://steamcommunity.com/gid/0"))

        # try profile urls
        sid = steamid.steam64_from_url('https://steamcommunity.com/profiles/[U:1:12]')
        self.assertEqual(sid, '76561197960265740')

        sid = steamid.steam64_from_url('https://steamcommunity.com/profiles/76561197960265740')
        self.assertEqual(sid, '76561197960265740')

        sid = steamid.steam64_from_url('https://steamcommunity.com/id/johnc')
        self.assertEqual(sid, '76561197960265740')


        # try group urls
        sid = steamid.steam64_from_url('https://steamcommunity.com/gid/[g:1:4]')
        self.assertEqual(sid, '103582791429521412')

        sid = steamid.steam64_from_url('https://steamcommunity.com/gid/103582791429521412')
        self.assertEqual(sid, '103582791429521412')

        sid = steamid.steam64_from_url('https://steamcommunity.com/groups/Valve')
        self.assertEqual(sid, '103582791429521412')

