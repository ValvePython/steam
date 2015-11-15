import re
import requests
from steam.enums import EType, EUniverse


class SteamID(object):
    """
    Object for converting steamID to its' various representations
    """

    ETypeChar = {
        0: 'I',
        1: 'U',
        2: 'M',
        3: 'G',
        4: 'A',
        5: 'P',
        6: 'C',
        7: 'g',
        8: 'T',
        8: 'c',
        8: 'L',
        10: 'a',
    }

    def __init__(self, *args, **kwargs):
        """
        The instance can be initialized with various parameters

        SteamID()  # invalid steamid
        SteamID(12345)  # accountid
        SteamID('12345')
        SteamID(id=12345, type='Invalid', universe='Invalid', instance=0)
        SteamID(103582791429521412)  # steam64
        SteamID('103582791429521412')
        SteamID('STEAM_1:0:2')  # steam2
        SteamID('[g:1:4]')  # steam3
        SteamID('http://steamcommunity.com/profiles/76561197968459473')

        # WARNING: vainty url resolving is fragile
        # it might break if community profile page changes
        # you should use the WebAPI to resolve them reliably
        SteamID('https://steamcommunity.com/id/drunkenf00l')
        """

        largs = len(args)

        if largs == 0 and len(kwargs) == 0:
            self.id = 0
            self.type = EType.Invalid
            self.universe = EUniverse.Invalid
            self.instance = 0
        elif largs > 0:
            if largs > 1:
                raise ValueError("Needed only 1 arg, got %d" % largs)

            value = str(args[0])

            # see if input is community url
            match = re.match(r'^https?://steamcommunity.com/'
                             r'(?P<type>id|profiles)/(?P<value>.*)/?$', value)
            if match:
                if match.group('type') == 'id':
                    page = requests.get(value).content
                    value = re.findall('steamid":"(\d+)",', page)
                    if not value:
                        raise ValueError("Unable to retrieve steamID")
                    value = value[0]
                else:
                    value = match.group('value')

            # numeric input
            if value.isdigit() or (value.startswith('-') and value[1:].isdigit()):
                value = int(value)
                if 0 > value:
                    raise ValueError("Expected positive int, got %d" % value)
                if value >= 2**64:
                    raise ValueError("Expected a 32/64 bit int")

                # 32 bit account id
                if value < 2**32:
                    self.id = value
                    self.type = EType.Individual
                    self.universe = EUniverse.Public
                    self.instance = 1
                # 64 bit
                else:
                    self.id = value & 0xFFffFFff
                    self.instance = (value >> 32) & 0xFFffF
                    self.type = EType((value >> 52) & 0xF)
                    self.universe = EUniverse((value >> 56) & 0xFF)

            # textual input e.g. [g:1:4]
            else:
                # try steam2
                match = re.match(r"^STEAM_(?P<universe>[01])"
                                 r":(?P<reminder>[0-1])"
                                 r":(?P<id>\d+)$", value
                                 )

                if match:
                    self.id = (int(match.group('id')) << 1) | int(match.group('reminder'))
                    self.universe = EUniverse(1)
                    self.type = EType(1)
                    self.instance = 1
                    return

                # try steam3
                typeChars = ''.join(self.ETypeChar.values())
                match = re.match(r"^\["
                                 r"(?P<type>[%s]):"        # type char
                                 r"(?P<universe>\d+):"     # universe
                                 r"(?P<id>\d+)"            # accountid
                                 r"(:(?P<instance>\d+))?"  # instance
                                 r"\]$" % typeChars, value
                                 )
                if match:
                    self.id = int(match.group('id'))
                    self.universe = EUniverse(int(match.group('universe')))
                    inverseETypeChar = dict((b, a) for (a, b) in self.ETypeChar.items())
                    self.type = EType(inverseETypeChar[match.group('type')])
                    self.instance = match.group('instance')
                    if self.instance is None:
                        if self.type in (EType.Individual, EType.GameServer):
                            self.instance = 1
                        else:
                            self.instance = 0
                    else:
                        self.instance = int(self.instance)
                    return

                raise ValueError("Expected a number or textual SteamID"
                                 " (e.g. [g:1:4], STEAM_0:1:1234), got %s" % repr(value)
                                 )

        elif len(kwargs):
            if 'id' not in kwargs:
                raise ValueError("Expected at least 'id' kwarg")

            self.id = int(kwargs['id'])
            assert self.id <= 0xffffFFFF, "id larger than 32bits"

            value = kwargs.get('type', 0)
            if type(value) in (int, EType):
                self.type = EType(value)
            else:
                self.type = EType[value.lower().capitalize()]

            value = kwargs.get('universe', 0)
            if type(value) in (int, EUniverse):
                self.universe = EUniverse(value)
            else:
                self.universe = EUniverse[value.lower().capitalize()]

            if 'instance' in kwargs:
                self.instance = kwargs['instance']
                assert self.instance <= 0xffffF, "instance larger than 20bits"
            else:
                if self.type in (EType.Individual, EType.GameServer):
                    self.instance = 1
                else:
                    self.instance = 0

    def __repr__(self):
        return "<%s(id=%s, type=%s, universe=%s, instance=%s)>" % (
            self.__class__.__name__,
            self.id,
            repr(self.type.name),
            repr(self.universe.name),
            self.instance,
            )

    def __str__(self):
        return str(self.as_64)

    @property
    def as_steam2(self):
        return "STEAM_0:%s:%s" % (
            self.id % 2,
            self.id >> 1,
            )

    @property
    def as_steam3(self):
        if self.type is EType.AnonGameServer:
            return "[%s:%s:%s:%s]" % (
                self.ETypeChar[self.type.value],
                self.universe.value,
                self.id,
                self.instance
                )
        else:
            return "[%s:%s:%s]" % (
                self.ETypeChar[self.type.value],
                self.universe.value,
                self.id,
                )

    @property
    def as_64(self):
        return ((self.universe.value << 56)
                | (self.type.value << 52)
                | (self.instance << 32)
                | self.id
                )

    @property
    def as_32(self):
        return self.id

    @property
    def community_url(self):
        suffix = {
            EType.Individual: "profiles/%s",
            EType.Clan: "gid/%s",
        }
        if self.type in suffix:
            url = "https://steamcommunity.com/%s" % suffix[self.type]
            return url % self.as_64
        return None
