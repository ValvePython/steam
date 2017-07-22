import re
from importlib import import_module

service_lookup = {
    'Broadcast':           'steam.protobufs.steammessages_broadcast_pb2',
    'Cloud':               'steam.protobufs.steammessages_cloud_pb2',
    'DNReport':            'steam.protobufs.steammessages_cloud_pb2',
    'Credentials':         'steam.protobufs.steammessages_credentials_pb2',
    'ContentBuilder':      'steam.protobufs.steammessages_depotbuilder_pb2',
    'DeviceAuth':          'steam.protobufs.steammessages_deviceauth_pb2',
    'Econ':                'steam.protobufs.steammessages_econ_pb2',
    'GameNotifications':   'steam.protobufs.steammessages_gamenotifications_pb2',
    'GameServers':         'steam.protobufs.steammessages_gameservers_pb2',
    'Inventory':           'steam.protobufs.steammessages_inventory_pb2',
    'Community':           'steam.protobufs.steammessages_linkfilter_pb2',
    'Offline':             'steam.protobufs.steammessages_offline_pb2',
    'Parental':            'steam.protobufs.steammessages_parental_pb2',
    'PartnerApps':         'steam.protobufs.steammessages_partnerapps_pb2',
    'PhysicalGoods':       'steam.protobufs.steammessages_physicalgoods_pb2',
    'PlayerClient':        'steam.protobufs.steammessages_player_pb2',
    'Player':              'steam.protobufs.steammessages_player_pb2',
    'PublishedFile':       'steam.protobufs.steammessages_publishedfile_pb2',
    'KeyEscrow':           'steam.protobufs.steammessages_secrets_pb2',
    'TwoFactor':           'steam.protobufs.steammessages_twofactor_pb2',
    'MsgTest':             'steam.protobufs.steammessages_unified_test_pb2',
    'Video':               'steam.protobufs.steammessages_video_pb2',
    'SiteLicense':         'steam.protobufs.steammessages_site_license_pb2',
    'UserAccount':         'steam.protobufs.steammessages_useraccount_pb2',
}

method_lookup = {
}

def get_um(method_name, response=False):
    """Get protobuf for given method name

    :param method_name: full method name (e.g. ``Player.GetGameBadgeLevels#1``)
    :type method_name: :class:`str`
    :param response: whether to return proto for response or request
    :type response: :class:`bool`
    :return: protobuf message
    """
    key = (method_name, response)

    if key not in method_lookup:
        match = re.findall(r'^([a-z]+)\.([a-z]+)#(\d)?$', method_name, re.I)
        if not match:
            return None

        interface, method, version = match[0]

        if interface not in service_lookup:
            raise None

        package = import_module(service_lookup[interface])

        service = getattr(package, interface, None)
        if service is None:
            return None

        for method_desc in service.GetDescriptor().methods:
            name = "%s.%s#%d" % (interface, method_desc.name, 1)

            method_lookup[(name, False)] = getattr(package, method_desc.input_type.full_name, None)
            method_lookup[(name, True)] = getattr(package, method_desc.output_type.full_name, None)

    return method_lookup[key]
