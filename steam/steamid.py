import re
from steam.enums import EType, EUniverse

ETypeCharMap = {
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


class SteamID(object):
    """
    Object for converting steamID to its' various representations
    """

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
        self.id = 0
        self.type = EType.Invalid
        self.universe = EUniverse.Invalid
        self.instance = 0

        if len(args) == 1:
            value = str(args[0])

            # numeric input
            if value.isdigit():
                value = int(value)

                # 32 bit account id
                if 0 < value < 2**32:
                    self.id = value
                    self.type = EType.Individual
                    self.universe = EUniverse.Public
                    self.instance = 1
                # 64 bit
                elif value < 2**64:
                    self.id = value & 0xFFffFFff
                    self.instance = (value >> 32) & 0xFFffF
                    self.type = EType((value >> 52) & 0xF)
                    self.universe = EUniverse((value >> 56) & 0xFF)

            # textual input e.g. [g:1:4]
            else:
                result = steam2_to_tuple(value) or steam3_to_tuple(value)

                if result:
                    (self.id,
                     self.type,
                     self.universe,
                     self.instance
                    ) = result

        elif len(kwargs):
            self.id = int(kwargs.get('id', 0))

            value = kwargs.get('type', 1)
            if type(value) in (int, EType):
                self.type = EType(value)
            else:
                self.type = EType[value.lower().capitalize()]

            value = kwargs.get('universe', 1)
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

    def __int__(self):
        return self.as_64

    def __eq__(self, other):
        return int(self) == int(other)

    def __ne__(self, other):
        return int(self) != int(other)

    def __lt__(self, other):
        return int(self) < int(other)

    def __le__(self, other):
        return int(self) <= int(other)

    def __gt__(self, other):
        return int(self) > int(other)

    def __ge__(self, other):
        return int(self) >= int(other)

    def __hash__(self):
        return hash(self.as_64)

    def is_valid(self):
        return (0 < self.id < 2**32
                and self.type is not EType.Invalid
                and self.universe is not EUniverse.Invalid
                )

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
                ETypeCharMap[self.type.value],
                self.universe.value,
                self.id,
                self.instance
                )
        else:
            return "[%s:%s:%s]" % (
                ETypeCharMap[self.type.value],
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


def steam2_to_tuple(value):
    match = re.match(r"^STEAM_(?P<universe>[01])"
                     r":(?P<reminder>[0-1])"
                     r":(?P<id>\d+)$", value
                     )

    if not match:
        return None

    steam32 = (int(match.group('id')) << 1) | int(match.group('reminder'))

    return (steam32, EType(1), EUniverse(1), 1)

def steam3_to_tuple(value):
    typeChars = ''.join(ETypeCharMap.values())
    match = re.match(r"^\["
                     r"(?P<type>[%s]):"        # type char
                     r"(?P<universe>\d+):"     # universe
                     r"(?P<id>\d+)"            # accountid
                     r"(:(?P<instance>\d+))?"  # instance
                     r"\]$" % typeChars, value
                     )
    if not match:
        return None

    steam32 = int(match.group('id'))

    universe = EUniverse(int(match.group('universe')))

    inverseETypeCharMap = dict((b, a) for (a, b) in ETypeCharMap.items())
    etype = EType(inverseETypeCharMap[match.group('type')])

    instance = match.group('instance')

    if instance is None:
        if etype in (EType.Individual, EType.GameServer):
            instance = 1
        else:
            instance = 0
    else:
        instance = int(instance)

    return (steam32, etype, universe, instance)

def steam64_from_url(url):
    """
    Takes a Steam Community url and returns steam64 or None

    Example URLs:
    ----
    https://steamcommunity.com/gid/[g:1:4]
    https://steamcommunity.com/gid/103582791429521412
    https://steamcommunity.com/groups/Valve
    https://steamcommunity.com/profiles/[U:1:12]
    https://steamcommunity.com/profiles/76561197960265740
    https://steamcommunity.com/id/johnc
    """

    match = re.match(r'^https?://steamcommunity.com/'
                     r'(?P<type>profiles|id|gid|groups)/(?P<value>.*)/?$', url)

    if not match:
        return None

    import requests

    if match.group('type') in ('id', 'profiles'):
        xml = requests.get("%s/?xml=1" % url).text
        match = re.findall('<steamID64>(\d+)</steamID64>', xml)
    else:
        xml = requests.get("%s/memberslistxml/?xml=1" % url).text
        match = re.findall('<groupID64>(\d+)</groupID64>', xml)

    if not match:
        return None

    return match[0]  # return matched steam64


def from_url(url):
    """
    Takes Steam community url and returns a SteamID instance or None

    Example URLs:
    ----
    https://steamcommunity.com/gid/[g:1:4]
    https://steamcommunity.com/gid/103582791429521412
    https://steamcommunity.com/groups/Valve
    https://steamcommunity.com/profiles/[U:1:12]
    https://steamcommunity.com/profiles/76561197960265740
    https://steamcommunity.com/id/johnc
    """

    steam64 = steam64_from_url(url)

    if steam64:
        return SteamID(steam64)

    return None
