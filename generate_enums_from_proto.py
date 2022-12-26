#!/usr/bin/env python

import re
from keyword import kwlist
from google.protobuf.internal.enum_type_wrapper import EnumTypeWrapper
from steam.enums import common as common_enums

kwlist = set(kwlist + ['None'])

_proto_modules = [
    'enums_pb2',
    'steammessages_auth_pb2',
    'steammessages_broadcast_pb2',
    'steammessages_chat_pb2',
    'steammessages_cloud_pb2',
    'steammessages_contentsystem_pb2',
    'steammessages_credentials_pb2',
    'steammessages_datapublisher_pb2',
    'steammessages_depotbuilder_pb2',
    'steammessages_deviceauth_pb2',
    'steammessages_econ_pb2',
    'steammessages_friendmessages_pb2',
    'steammessages_gamenotifications_pb2',
    'steammessages_gameservers_pb2',
    'steammessages_inventory_pb2',
    'steammessages_linkfilter_pb2',
    'steammessages_lobbymatchmaking_pb2',
    'steammessages_marketingmessages_pb2',
    'steammessages_market_pb2',
    'steammessages_offline_pb2',
    'steammessages_parental_pb2',
    'steammessages_parties_pb2',
    'steammessages_partnerapps_pb2',
    'steammessages_physicalgoods_pb2',
    'steammessages_player_pb2',
    'steammessages_publishedfile_pb2',
    'steammessages_qms_pb2',
    'steammessages_remoteplay_pb2',
    'steammessages_secrets_pb2',
    'steammessages_shader_pb2',
    'steammessages_site_license_pb2',
    'steammessages_star_pb2',
    'steammessages_steamtv_pb2',
    'steammessages_storebrowse_pb2',
    'steammessages_store_pb2',
    'steammessages_timedtrial_pb2',
    'steammessages_twofactor_pb2',
    'steammessages_unified_base_pb2',
    'steammessages_unified_test_pb2',
    'steammessages_useraccount_pb2',
    'steammessages_video_pb2',
    'steammessages_webui_friends_pb2',
    'steammessages_workshop_pb2',
]

_proto_module = __import__("steam.protobufs", globals(), locals(), _proto_modules, 0)

classes = {}

for name in _proto_modules:

    proto = getattr(_proto_module, name)
    gvars = globals()

    for class_name, value in proto.__dict__.items():
        if not isinstance(value, EnumTypeWrapper) or hasattr(common_enums, class_name):
            continue

        attrs_starting_with_number = False
        attrs = {}

        for ikey, ivalue in value.items():
            ikey = re.sub(r'^(k_)?(%s_)?' % class_name, '', ikey)
            attrs[ikey] = ivalue

            if ikey[0:1].isdigit() or ikey in kwlist:
                attrs_starting_with_number = True

        classes[class_name] = attrs, attrs_starting_with_number

# print out enums as python Enum
print("from steam.enums.base import SteamIntEnum")

for class_name, (attrs, attrs_starting_with_number) in sorted(classes.items(), key=lambda x: x[0].lower()):
        if attrs_starting_with_number:
            print("\n%s = SteamIntEnum(%r, {" % (class_name, class_name))
            for ikey, ivalue in attrs.items():
                print("    %r: %r," % (ikey, ivalue))
            print("    })")
        else:
            print("\nclass {class_name}(SteamIntEnum):".format(class_name=class_name))
            for ikey, ivalue in attrs.items():
                print("    {} = {}".format(ikey, ivalue))

print("\n__all__ = [")

for class_name in sorted(classes, key=lambda x: x.lower()):
    print("    %r," % class_name)

print("    ]")
