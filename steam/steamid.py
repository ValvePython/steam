import enum
import re
import requests


class SteamID(object):
    """
    Object for converting steamID to its' various representations
    """
    # Enums

    class EUniverse(enum.Enum):
        Invalid = 0
        Public = 1
        Beta = 2
        Internal = 3
        Dev = 4

    class EType(enum.Enum):
        Invalid = 0
        Individual = 1
        Multiseat = 2
        GameServer = 3
        AnonGameServer = 4
        Pending = 5
        ContentServer = 6
        Clan = 7
        Chat = 8
        ConsoleUser = 9
        AnonUser = 10

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
        SteamID('[g:1:4]')  # steam3
        SteamID('https://steamcommunity.com/id/drunkenf00l')  # vanity url
        SteamID('http://steamcommunity.com/profiles/76561197968459473')

        """

        largs = len(args)
        lkwargs = len(kwargs)

        if largs == 0 and lkwargs == 0:
            self.id = 0
            self.type = self.EType.Invalid
            self.universe = self.EType.Invalid
            self.instance = 0
        elif largs > 0:
            if largs > 1:
                raise ValueError("Needed only 1 arg, got %d" % largs)

            value = str(args[0])

            # see if input is community url
            match = re.match(r'^https?://steamcommunity.com/(?P<type>id|profiles)/(?P<value>.*)/?$', value)
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
            if value.isdigit():
                value = int(value)
                if 0 > value:
                    raise ValueError("Expected positive int, got %d" % value)
                if value > 2**64-1:
                    raise ValueError("Expected a 32/64 bit int")

                # 32 bit account id
                if value < 2**32-1:
                    self.id = value
                    self.type = self.EType.Individual
                    self.universe = self.EUniverse.Public
                    self.instance = 1
                # 64 bit
                else:
                    self.id = value & 0xFFffFFff
                    self.instance = (value >> 32) & 0xFFffF
                    self.type = self.EType((value >> 52) & 0xF)
                    self.universe = self.EUniverse((value >> 56) & 0xFF)

            # textual input e.g. [g:1:4]
            else:
                typeChars = ''.join(self.ETypeChar.values())
                match = re.match(r"^\[(?P<type>[%s]):(?P<universe>\d+):(?P<id>\d+)(:(?P<instance>\d+))?\]$" % typeChars, value)
                if not match:
                    raise ValueError("Expected a number or textual SteamID (e.g. [g:1:4]), got %s" % repr(value))

                self.id = int(match.group('id'))
                self.universe = self.EUniverse(int(match.group('universe')))
                inverseETypeChar = dict((b, a) for (a, b) in self.ETypeChar.items())
                self.type = self.EType(inverseETypeChar[match.group('type')])
                self.instance = match.group('instance')
                if self.instance is None:
                    if self.type in (self.EType.Individual, self.EType.GameServer):
                        self.instance = 1
                    else:
                        self.instance = 0
                else:
                    self.instance = int(self.instance)

        elif lkwargs > 0:
            if 'id' not in kwargs:
                raise ValueError("Expected at least 'id' kwarg")

            self.id = int(kwargs['id'])

            for kwname in 'type', 'universe':
                if kwname in kwargs:
                    value = kwargs[kwname]
                    kwenum = getattr(self, "E%s" % kwname.capitalize())

                    resolved = getattr(kwenum, value, None)
                    if resolved is None:
                        try:
                            resolved = kwenum(value)
                        except ValueError:
                            raise ValueError(
                                "Invalid value for kwarg '%s', see SteamID.E%s" %
                                (kwname, kwname.capitalize())
                                )
                    setattr(self, kwname, resolved)

            if self.type in (self.EType.Individual, self.EType.GameServer):
                self.instance = 1
            else:
                self.instance = 0

    def __repr__(self):
        return "%s(id=%s, type=%s, universe=%s, instance=%s)" % (
            self.__class__.__name__,
            self.id,
            repr(self.type.name),
            repr(self.universe.name),
            self.instance,
            )

    def __str__(self):
        return self.as_64

    @property
    def as_steam3(self):
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
        return "STEAM_0:%s:%s" % (
            self.id % 2,
            self.id >> 1,
            )

    @property
    def community_url(self):
        suffix = {
            self.EType.Individual: "profiles/%s",
            self.EType.Clan: "gid/%s",
        }
        if self.type in suffix:
            url = "http://steamcommunity.com/%s" % suffix[self.type]
            return url % self.as_64
        return ''
