import struct
import json
import sys
import re
import requests
from steam.enums.base import SteamIntEnum
from steam.enums import EType, EUniverse, EInstanceFlag
from steam.core.crypto import md5_hash
from steam.utils.web import make_requests_session

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
    L = EType.Chat # lobby chat, 'c' for clan chat
    c = EType.Chat # clan chat
    a = EType.AnonUser

    def __str__(self):
        return self.name

ETypeChars = ''.join(ETypeChar.__members__.keys())

_icode_hex       = "0123456789abcdef"
_icode_custom    = "bcdfghjkmnpqrtvw"
_icode_all_valid = _icode_hex + _icode_custom
_icode_map       = dict(zip(_icode_hex,    _icode_custom))
_icode_map_inv   = dict(zip(_icode_custom, _icode_hex   ))
_csgofrcode_chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'


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
    EType = EType                  #: reference to EType
    EUniverse = EUniverse          #: reference to EUniverse
    EInstanceFlag = EInstanceFlag  #: reference to EInstanceFlag

    def __new__(cls, *args, **kwargs):
        steam64 = make_steam64(*args, **kwargs)
        return super(SteamID, cls).__new__(cls, steam64)

    def __init__(self, *args, **kwargs):
        pass

    def __str__(self):
        return str(int(self))

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
    def account_id(self):
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
        typechar = str(ETypeChar(self.type))
        instance = None

        if self.type in (EType.AnonGameServer, EType.Multiseat):
            instance = self.instance
        elif self.type == EType.Individual:
            if self.instance != 1:
                instance = self.instance
        elif self.type == EType.Chat:
            if self.instance & EInstanceFlag.Clan:
                typechar = 'c'
            elif self.instance & EInstanceFlag.Lobby:
                typechar = 'L'
            else:
                typechar = 'T'

        parts = [typechar, int(self.universe), self.id]

        if instance is not None:
            parts.append(instance)

        return '[%s]' % (':'.join(map(str, parts)))

    @property
    def as_invite_code(self):
        """
        :return: s.team invite code format (e.g. ``cv-dgb``)
        :rtype: :class:`str`
        """
        if self.type == EType.Individual and self.is_valid():
            def repl_mapper(x):
                return _icode_map[x.group()]

            invite_code = re.sub("["+_icode_hex+"]", repl_mapper, "%x" % self.id)
            split_idx = len(invite_code) // 2

            if split_idx:
                invite_code = invite_code[:split_idx] + '-' + invite_code[split_idx:]

            return invite_code

    @property
    def as_csgo_friend_code(self):
        """
        :return: CS:GO Friend code (e.g. ``AEBJA-ABDC``)
        :rtype: :class:`str`
        """
        if self.type != EType.Individual or not self.is_valid():
            return

        h = b'CSGO' + struct.pack('>L', self.account_id)
        h, = struct.unpack('<L', md5_hash(h[::-1])[:4])
        steamid = self.as_64
        result = 0

        for i in range(8):
            id_nib = (steamid >> (i * 4)) & 0xF
            hash_nib = (h >> i) & 0x1
            a = (result << 4) | id_nib

            result = ((result >> 28) << 32) | a
            result = ((result >> 31) << 32) | ((a << 1) | hash_nib)

        result, = struct.unpack('<Q', struct.pack('>Q', result))
        code = ''

        for i in range(13):
            if i in (4, 9):
                code += '-'

            code += _csgofrcode_chars[result & 31]
            result = result >> 5

        return code[5:]

    @property
    def invite_url(self):
        """
        :return: e.g ``https://s.team/p/cv-dgb``
        :rtype: :class:`str`
        """
        code = self.as_invite_code
        if code:
            return "https://s.team/p/" + code

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
        Check whether this SteamID is valid

        :rtype: :py:class:`bool`
        """
        if self.type == EType.Invalid or self.type >= EType.Max:
            return False

        if self.universe == EUniverse.Invalid or self.universe >= EUniverse.Max:
            return False

        if self.type == EType.Individual:
            if self.id == 0 or self.instance > 4:
                return False

        if self.type == EType.Clan:
            if self.id == 0 or self.instance != 0:
                return False

        if self.type == EType.GameServer:
            if self.id == 0:
                return False

        if self.type == EType.AnonGameServer:
            if self.id == 0 and self.instance == 0:
                return False

        return True


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
                accountid = int(value & 0xFFFFFFFF)
                instance = int((value >> 32) & 0xFFFFF)
                etype = int((value >> 52) & 0xF)
                universe = int((value >> 56) & 0xFF)
            # invalid account id
            else:
                accountid = 0

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
                     r"(?P<type>[i%s]):"        # type char
                     r"(?P<universe>[0-4]):"     # universe
                     r"(?P<id>\d{1,10})"            # accountid
                     r"(:(?P<instance>\d+))?"  # instance
                     r"\]$" % ETypeChars,
                     value
                     )
    if not match:
        return None

    steam32 = int(match.group('id'))
    universe = EUniverse(int(match.group('universe')))
    typechar = match.group('type').replace('i', 'I')
    etype = EType(ETypeChar[typechar])
    instance = match.group('instance')

    if typechar in 'gT':
        instance = 0
    elif instance is not None:
        instance = int(instance)
    elif typechar == 'L':
        instance = EInstanceFlag.Lobby
    elif typechar == 'c':
        instance = EInstanceFlag.Clan
    elif etype in (EType.Individual, EType.GameServer):
        instance = 1
    else:
        instance = 0

    instance = int(instance)

    return (steam32, etype, universe, instance)

def from_invite_code(code, universe=EUniverse.Public):
    """
    Invites urls can be generated at https://steamcommunity.com/my/friends/add

    :param code: invite code (e.g. ``https://s.team/p/cv-dgb``, ``cv-dgb``)
    :type  code: :class:`str`
    :param universe: Steam universe (default: ``Public``)
    :type  universe: :class:`EType`
    :return: (accountid, type, universe, instance)
    :rtype: :class:`tuple` or :class:`None`
    """
    if not code:
        return None

    m = re.match(r'(https?://s\.team/p/(?P<code1>[\-'+_icode_all_valid+']+))'
                 r'|(?P<code2>[\-'+_icode_all_valid+']+$)'
                 , code)
    if not m:
        return None

    code = (m.group('code1') or m.group('code2')).replace('-', '')

    def repl_mapper(x):
        return _icode_map_inv[x.group()]

    accountid = int(re.sub("["+_icode_custom+"]", repl_mapper, code), 16)

    if 0 < accountid < 2**32:
        return SteamID(accountid, EType.Individual, EUniverse(universe), 1)

SteamID.from_invite_code = staticmethod(from_invite_code)

def from_csgo_friend_code(code, universe=EUniverse.Public):
    """
    Takes CS:GO friend code and returns SteamID

    :param code: CS:GO friend code (e.g. ``AEBJA-ABDC``)
    :type  code: :class:`str`
    :param universe: Steam universe (default: ``Public``)
    :type  universe: :class:`EType`
    :return: SteamID instance
    :rtype: :class:`.SteamID` or :class:`None`
    """
    if not re.match(r'^['+_csgofrcode_chars+'\-]{10}$', code):
        return None

    code = ('AAAA-' + code).replace('-', '')
    result = 0

    for i in range(13):
        index = _csgofrcode_chars.find(code[i])
        if index == -1:
            return None
        result = result | (index << 5 * i)

    result, = struct.unpack('<Q', struct.pack('>Q', result))
    accountid = 0

    for i in range(8):
        result = result >> 1
        id_nib = result & 0xF
        result = result >> 4
        accountid = (accountid << 4) | id_nib

    return SteamID(accountid, EType.Individual, EUniverse(universe), 1)

SteamID.from_csgo_friend_code = staticmethod(from_csgo_friend_code)

def steam64_from_url(url, http_timeout=30):
    """
    Takes a Steam Community url and returns steam64 or None

    .. warning::
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
        https://steamcommunity.com/user/cv-dgb/
    """

    match = re.match(r'^(?P<clean_url>https?://steamcommunity.com/'
                     r'(?P<type>profiles|id|gid|groups|user)/(?P<value>.*?))(?:/(?:.*)?)?$', url)

    if not match:
        return None

    web = make_requests_session()

    try:
        # user profiles
        if match.group('type') in ('id', 'profiles', 'user'):
            text = web.get(match.group('clean_url'), timeout=http_timeout).text
            data_match = re.search("g_rgProfileData = (?P<json>{.*?});[ \t\r]*\n", text)

            if data_match:
                data = json.loads(data_match.group('json'))
                return int(data['steamid'])
        # group profiles
        else:
            text = web.get(match.group('clean_url'), timeout=http_timeout).text
            data_match = re.search("OpenGroupChat\( *'(?P<steamid>\d+)'", text)

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

    steam64 = steam64_from_url(url, http_timeout)

    if steam64:
        return SteamID(steam64)

    return None

SteamID.from_url = staticmethod(from_url)
