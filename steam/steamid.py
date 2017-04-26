import json
import sys
import re
import requests
from steam.enums.base import SteamIntEnum
from steam.enums import EType, EUniverse
from steam.util.web import make_requests_session

if sys.version_info < (3,):
    intBase = long
else:
    intBase = int

class ETypeChar(SteamIntEnum):
    I = EType.Invalid
    U = EType.Individual
    M = EType.Multiseat
    G = EType.GameServer
    A = EType.AnonGameServer
    P = EType.Pending
    C = EType.ContentServer
    g = EType.Clan
    T = EType.Chat
    c = EType.Chat
    L = EType.Chat
    a = EType.AnonUser

    def __str__(self):
        return self.name

ETypeChars = ''.join(map(str, list(ETypeChar)))


class SteamID(intBase):
    """
    Object for converting steamID to its' various representations

    .. code:: python

        SteamID()  # invalid steamid
        SteamID(12345)  # accountid
        SteamID('12345')
        SteamID(id=12345, type='Invalid', universe='Invalid', instance=0)
        SteamID(103582791429521412)  # steam64
        SteamID('103582791429521412')
        SteamID('STEAM_1:0:2')  # steam2
        SteamID('[g:1:4]')  # steam3
    """
    EType = EType               #: reference to EType
    EUniverse = EUniverse       #: reference to EUniverse

    def __new__(cls, *args, **kwargs):
        steam64 = make_steam64(*args, **kwargs)
        return super(SteamID, cls).__new__(cls, steam64)

    def __init__(self, *args, **kwargs):
        pass

    def __repr__(self):
        return "%s(id=%s, type=%s, universe=%s, instance=%s)" % (
            self.__class__.__name__,
            self.id,
            repr(self.type.name),
            repr(self.universe.name),
            self.instance,
            )

    @property
    def id(self):
        """
        :return: account id
        :rtype: :class:`int`
        """
        return int(self) & 0xFFffFFff

    @property
    def instance(self):
        """
        :rtype: :class:`int`
        """
        return (int(self) >> 32) & 0xFFffF

    @property
    def type(self):
        """
        :rtype: :py:class:`steam.enum.EType`
        """
        return EType((int(self) >> 52) & 0xF)

    @property
    def universe(self):
        """
        :rtype: :py:class:`steam.enum.EUniverse`
        """
        return EUniverse((int(self) >> 56) & 0xFF)

    @property
    def as_32(self):
        """
        :return: account id
        :rtype: :class:`int`
        """
        return self.id

    @property
    def as_64(self):
        """
        :return: steam64 format
        :rtype: :class:`int`
        """
        return int(self)

    @property
    def as_steam2(self):
        """
        :return: steam2 format (e.g ``STEAM_1:0:1234``)
        :rtype: :class:`str`

        .. note::
            ``STEAM_X:Y:Z``. The value of ``X`` should represent the universe, or ``1``
            for ``Public``. However, there was a bug in GoldSrc and Orange Box games
            and ``X`` was ``0``. If you need that format use :attr:`SteamID.as_steam2_zero`


        """
        return "STEAM_%d:%d:%d" % (
            int(self.universe),
            self.id % 2,
            self.id >> 1,
            )

    @property
    def as_steam2_zero(self):
        """
        For GoldSrc and Orange Box games.
        See :attr:`SteamID.as_steam2`

        :return: steam2 format (e.g ``STEAM_0:0:1234``)
        :rtype: :class:`str`
        """
        return self.as_steam2.replace("_1", "_0")

    @property
    def as_steam3(self):
        """
        :return: steam3 format (e.g ``[U:1:1234]``)
        :rtype: :class:`str`
        """
        if self.type is EType.AnonGameServer:
            return "[%s:%s:%s:%s]" % (
                str(ETypeChar(self.type)),
                int(self.universe),
                self.id,
                self.instance
                )
        else:
            return "[%s:%s:%s]" % (
                str(ETypeChar(self.type)),
                int(self.universe),
                self.id,
                )

    @property
    def community_url(self):
        """
        :return: e.g https://steamcommunity.com/profiles/123456789
        :rtype: :class:`str`
        """
        suffix = {
            EType.Individual: "profiles/%s",
            EType.Clan: "gid/%s",
        }
        if self.type in suffix:
            url = "https://steamcommunity.com/%s" % suffix[self.type]
            return url % self.as_64

        return None

    def is_valid(self):
        """
        :rtype: :py:class:`bool`
        """
        return (self.id > 0
                and self.type is not EType.Invalid
                and self.universe is not EUniverse.Invalid
                )


def make_steam64(id=0, *args, **kwargs):
    """
    Returns steam64 from various other representations.

    .. code:: python

        make_steam64()  # invalid steamid
        make_steam64(12345)  # accountid
        make_steam64('12345')
        make_steam64(id=12345, type='Invalid', universe='Invalid', instance=0)
        make_steam64(103582791429521412)  # steam64
        make_steam64('103582791429521412')
        make_steam64('STEAM_1:0:2')  # steam2
        make_steam64('[g:1:4]')  # steam3
    """

    accountid = id
    etype = EType.Invalid
    universe = EUniverse.Invalid
    instance = None

    if len(args) == 0 and len(kwargs) == 0:
        value = str(accountid)

        # numeric input
        if value.isdigit():
            value = int(value)

            # 32 bit account id
            if 0 < value < 2**32:
                accountid = value
                etype = EType.Individual
                universe = EUniverse.Public
            # 64 bit
            elif value < 2**64:
                return value

        # textual input e.g. [g:1:4]
        else:
            result = steam2_to_tuple(value) or steam3_to_tuple(value)

            if result:
                (accountid,
                 etype,
                 universe,
                 instance,
                 ) = result
            else:
                accountid = 0

    elif len(args) > 0:
        length = len(args)
        if length == 1:
            etype, = args
        elif length == 2:
            etype, universe = args
        elif length == 3:
            etype, universe, instance = args
        else:
            raise TypeError("Takes at most 4 arguments (%d given)" % length)

    if len(kwargs) > 0:
        etype = kwargs.get('type', etype)
        universe = kwargs.get('universe', universe)
        instance = kwargs.get('instance', instance)

    etype = (EType(etype)
             if isinstance(etype, (int, EType))
             else EType[etype]
             )

    universe = (EUniverse(universe)
                if isinstance(universe, (int, EUniverse))
                else EUniverse[universe]
                )

    if instance is None:
        instance = 1 if etype in (EType.Individual, EType.GameServer) else 0

    assert instance <= 0xffffF, "instance larger than 20bits"

    return (universe << 56) | (etype << 52) | (instance << 32) | accountid


def steam2_to_tuple(value):
    """
    :param value: steam2 (e.g. ``STEAM_1:0:1234``)
    :type value: :class:`str`
    :return: (accountid, type, universe, instance)
    :rtype: :class:`tuple` or :class:`None`

    .. note::
        The universe will be always set to ``1``. See :attr:`SteamID.as_steam2`
    """
    match = re.match(r"^STEAM_(?P<universe>\d+)"
                     r":(?P<reminder>[0-1])"
                     r":(?P<id>\d+)$", value
                     )

    if not match:
        return None

    steam32 = (int(match.group('id')) << 1) | int(match.group('reminder'))
    universe = int(match.group('universe'))

    # Games before orange box used to incorrectly display universe as 0, we support that
    if universe == 0:
        universe = 1

    return (steam32, EType(1), EUniverse(universe), 1)


def steam3_to_tuple(value):
    """
    :param value: steam3 (e.g. ``[U:1:1234]``)
    :type value: :class:`str`
    :return: (accountid, type, universe, instance)
    :rtype: :class:`tuple` or :class:`None`
    """
    match = re.match(r"^\["
                     r"(?P<type>[%s]):"        # type char
                     r"(?P<universe>\d+):"     # universe
                     r"(?P<id>\d+)"            # accountid
                     r"(:(?P<instance>\d+))?"  # instance
                     r"\]$" % ETypeChars,
                     value
                     )
    if not match:
        return None

    steam32 = int(match.group('id'))
    universe = EUniverse(int(match.group('universe')))
    etype = ETypeChar[match.group('type')]
    instance = match.group('instance')

    if instance is None:
        if etype in (EType.Individual, EType.GameServer):
            instance = 1
        else:
            instance = 0
    else:
        instance = int(instance)

    return (steam32, etype, universe, instance)

def steam64_from_url(url, http_timeout=30):
    """
    Takes a Steam Community url and returns steam64 or None

    .. note::
        Each call makes a http request to ``steamcommunity.com``

    .. note::
        For a reliable resolving of vanity urls use ``ISteamUser.ResolveVanityURL`` web api

    :param url: steam community url
    :type url: :class:`str`
    :param http_timeout: how long to wait on http request before turning ``None``
    :type http_timeout: :class:`int`
    :return: steam64, or ``None`` if ``steamcommunity.com`` is down
    :rtype: :class:`int` or :class:`None`

    Example URLs::

        https://steamcommunity.com/gid/[g:1:4]
        https://steamcommunity.com/gid/103582791429521412
        https://steamcommunity.com/groups/Valve
        https://steamcommunity.com/profiles/[U:1:12]
        https://steamcommunity.com/profiles/76561197960265740
        https://steamcommunity.com/id/johnc
    """

    match = re.match(r'^(?P<clean_url>https?://steamcommunity.com/'
                     r'(?P<type>profiles|id|gid|groups)/(?P<value>.*?))(?:/(?:.*)?)?$', url)

    if not match:
        return None

    web = make_requests_session()

    try:
        # user profiles
        if match.group('type') in ('id', 'profiles'):
            text = web.get(match.group('clean_url'), timeout=http_timeout).text
            data_match = re.search("g_rgProfileData = (?P<json>.*?);", text)

            if data_match:
                data = json.loads(data_match.group('json'))
                return int(data['steamid'])
        # group profiles
        else:
            text = web.get(match.group('clean_url'), timeout=http_timeout).text
            data_match = re.search("'steam://friends/joinchat/(?P<steamid>\d+)'", text)

            if data_match:
                return int(data_match.group('steamid'))
    except requests.exceptions.RequestException:
        return None


def from_url(url, http_timeout=30):
    """
    Takes Steam community url and returns a SteamID instance or ``None``

    See :py:func:`steam64_from_url` for details

    :param url: steam community url
    :type url: :class:`str`
    :param http_timeout: how long to wait on http request before turning ``None``
    :type http_timeout: :class:`int`
    :return: `SteamID` instance
    :rtype: :py:class:`steam.SteamID` or :class:`None`

    """

    steam64 = steam64_from_url(url)

    if steam64:
        return SteamID(steam64)

    return None

SteamID.from_url = staticmethod(from_url)
