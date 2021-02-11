# @generated by generate_proto_mypy_stubs.py.  Do not edit!
import sys
from abc import (
    ABCMeta as abc___ABCMeta,
    abstractmethod as abc___abstractmethod,
)

from concurrent.futures import (
    Future as concurrent___futures___Future,
)

from google.protobuf.descriptor import (
    Descriptor as google___protobuf___descriptor___Descriptor,
    FileDescriptor as google___protobuf___descriptor___FileDescriptor,
)

from google.protobuf.internal.containers import (
    RepeatedCompositeFieldContainer as google___protobuf___internal___containers___RepeatedCompositeFieldContainer,
)

from google.protobuf.message import (
    Message as google___protobuf___message___Message,
)

from google.protobuf.service import (
    RpcChannel as google___protobuf___service___RpcChannel,
    RpcController as google___protobuf___service___RpcController,
    Service as google___protobuf___service___Service,
)

from typing import (
    Callable as typing___Callable,
    Iterable as typing___Iterable,
    Optional as typing___Optional,
    Text as typing___Text,
)

from typing_extensions import (
    Literal as typing_extensions___Literal,
)


builtin___bool = bool
builtin___bytes = bytes
builtin___float = float
builtin___int = int


DESCRIPTOR: google___protobuf___descriptor___FileDescriptor = ...

class CPhysicalGoods_RegisterSteamController_Request(google___protobuf___message___Message):
    DESCRIPTOR: google___protobuf___descriptor___Descriptor = ...
    serial_number: typing___Text = ...
    controller_code: typing___Text = ...

    def __init__(self,
        *,
        serial_number : typing___Optional[typing___Text] = None,
        controller_code : typing___Optional[typing___Text] = None,
        ) -> None: ...
    def HasField(self, field_name: typing_extensions___Literal[u"controller_code",b"controller_code",u"serial_number",b"serial_number"]) -> builtin___bool: ...
    def ClearField(self, field_name: typing_extensions___Literal[u"controller_code",b"controller_code",u"serial_number",b"serial_number"]) -> None: ...
type___CPhysicalGoods_RegisterSteamController_Request = CPhysicalGoods_RegisterSteamController_Request

class CPhysicalGoods_RegisterSteamController_Response(google___protobuf___message___Message):
    DESCRIPTOR: google___protobuf___descriptor___Descriptor = ...

    def __init__(self,
        ) -> None: ...
type___CPhysicalGoods_RegisterSteamController_Response = CPhysicalGoods_RegisterSteamController_Response

class CPhysicalGoods_CompleteSteamControllerRegistration_Request(google___protobuf___message___Message):
    DESCRIPTOR: google___protobuf___descriptor___Descriptor = ...
    serial_number: typing___Text = ...
    controller_code: typing___Text = ...

    def __init__(self,
        *,
        serial_number : typing___Optional[typing___Text] = None,
        controller_code : typing___Optional[typing___Text] = None,
        ) -> None: ...
    def HasField(self, field_name: typing_extensions___Literal[u"controller_code",b"controller_code",u"serial_number",b"serial_number"]) -> builtin___bool: ...
    def ClearField(self, field_name: typing_extensions___Literal[u"controller_code",b"controller_code",u"serial_number",b"serial_number"]) -> None: ...
type___CPhysicalGoods_CompleteSteamControllerRegistration_Request = CPhysicalGoods_CompleteSteamControllerRegistration_Request

class CPhysicalGoods_CompleteSteamControllerRegistration_Response(google___protobuf___message___Message):
    DESCRIPTOR: google___protobuf___descriptor___Descriptor = ...

    def __init__(self,
        ) -> None: ...
type___CPhysicalGoods_CompleteSteamControllerRegistration_Response = CPhysicalGoods_CompleteSteamControllerRegistration_Response

class CPhysicalGoods_QueryAccountsRegisteredToSerial_Request(google___protobuf___message___Message):
    DESCRIPTOR: google___protobuf___descriptor___Descriptor = ...
    serial_number: typing___Text = ...
    controller_code: typing___Text = ...

    def __init__(self,
        *,
        serial_number : typing___Optional[typing___Text] = None,
        controller_code : typing___Optional[typing___Text] = None,
        ) -> None: ...
    def HasField(self, field_name: typing_extensions___Literal[u"controller_code",b"controller_code",u"serial_number",b"serial_number"]) -> builtin___bool: ...
    def ClearField(self, field_name: typing_extensions___Literal[u"controller_code",b"controller_code",u"serial_number",b"serial_number"]) -> None: ...
type___CPhysicalGoods_QueryAccountsRegisteredToSerial_Request = CPhysicalGoods_QueryAccountsRegisteredToSerial_Request

class CPhysicalGoods_QueryAccountsRegisteredToSerial_Accounts(google___protobuf___message___Message):
    DESCRIPTOR: google___protobuf___descriptor___Descriptor = ...
    accountid: builtin___int = ...
    registration_complete: builtin___bool = ...

    def __init__(self,
        *,
        accountid : typing___Optional[builtin___int] = None,
        registration_complete : typing___Optional[builtin___bool] = None,
        ) -> None: ...
    def HasField(self, field_name: typing_extensions___Literal[u"accountid",b"accountid",u"registration_complete",b"registration_complete"]) -> builtin___bool: ...
    def ClearField(self, field_name: typing_extensions___Literal[u"accountid",b"accountid",u"registration_complete",b"registration_complete"]) -> None: ...
type___CPhysicalGoods_QueryAccountsRegisteredToSerial_Accounts = CPhysicalGoods_QueryAccountsRegisteredToSerial_Accounts

class CPhysicalGoods_QueryAccountsRegisteredToSerial_Response(google___protobuf___message___Message):
    DESCRIPTOR: google___protobuf___descriptor___Descriptor = ...

    @property
    def accounts(self) -> google___protobuf___internal___containers___RepeatedCompositeFieldContainer[type___CPhysicalGoods_QueryAccountsRegisteredToSerial_Accounts]: ...

    def __init__(self,
        *,
        accounts : typing___Optional[typing___Iterable[type___CPhysicalGoods_QueryAccountsRegisteredToSerial_Accounts]] = None,
        ) -> None: ...
    def ClearField(self, field_name: typing_extensions___Literal[u"accounts",b"accounts"]) -> None: ...
type___CPhysicalGoods_QueryAccountsRegisteredToSerial_Response = CPhysicalGoods_QueryAccountsRegisteredToSerial_Response

class CPhysicalGoods_SteamControllerSetConfig_ControllerConfig(google___protobuf___message___Message):
    DESCRIPTOR: google___protobuf___descriptor___Descriptor = ...
    appidorname: typing___Text = ...
    publishedfileid: builtin___int = ...
    templatename: typing___Text = ...

    def __init__(self,
        *,
        appidorname : typing___Optional[typing___Text] = None,
        publishedfileid : typing___Optional[builtin___int] = None,
        templatename : typing___Optional[typing___Text] = None,
        ) -> None: ...
    def HasField(self, field_name: typing_extensions___Literal[u"appidorname",b"appidorname",u"publishedfileid",b"publishedfileid",u"templatename",b"templatename"]) -> builtin___bool: ...
    def ClearField(self, field_name: typing_extensions___Literal[u"appidorname",b"appidorname",u"publishedfileid",b"publishedfileid",u"templatename",b"templatename"]) -> None: ...
type___CPhysicalGoods_SteamControllerSetConfig_ControllerConfig = CPhysicalGoods_SteamControllerSetConfig_ControllerConfig

class CPhysicalGoods_SteamControllerSetConfig_Request(google___protobuf___message___Message):
    DESCRIPTOR: google___protobuf___descriptor___Descriptor = ...
    serial_number: typing___Text = ...
    controller_code: typing___Text = ...
    accountid: builtin___int = ...
    controller_type: builtin___int = ...
    only_for_this_serial: builtin___bool = ...

    @property
    def configurations(self) -> google___protobuf___internal___containers___RepeatedCompositeFieldContainer[type___CPhysicalGoods_SteamControllerSetConfig_ControllerConfig]: ...

    def __init__(self,
        *,
        serial_number : typing___Optional[typing___Text] = None,
        controller_code : typing___Optional[typing___Text] = None,
        accountid : typing___Optional[builtin___int] = None,
        configurations : typing___Optional[typing___Iterable[type___CPhysicalGoods_SteamControllerSetConfig_ControllerConfig]] = None,
        controller_type : typing___Optional[builtin___int] = None,
        only_for_this_serial : typing___Optional[builtin___bool] = None,
        ) -> None: ...
    def HasField(self, field_name: typing_extensions___Literal[u"accountid",b"accountid",u"controller_code",b"controller_code",u"controller_type",b"controller_type",u"only_for_this_serial",b"only_for_this_serial",u"serial_number",b"serial_number"]) -> builtin___bool: ...
    def ClearField(self, field_name: typing_extensions___Literal[u"accountid",b"accountid",u"configurations",b"configurations",u"controller_code",b"controller_code",u"controller_type",b"controller_type",u"only_for_this_serial",b"only_for_this_serial",u"serial_number",b"serial_number"]) -> None: ...
type___CPhysicalGoods_SteamControllerSetConfig_Request = CPhysicalGoods_SteamControllerSetConfig_Request

class CPhysicalGoods_SteamControllerSetConfig_Response(google___protobuf___message___Message):
    DESCRIPTOR: google___protobuf___descriptor___Descriptor = ...

    def __init__(self,
        ) -> None: ...
type___CPhysicalGoods_SteamControllerSetConfig_Response = CPhysicalGoods_SteamControllerSetConfig_Response

class CPhysicalGoods_SteamControllerGetConfig_Request(google___protobuf___message___Message):
    DESCRIPTOR: google___protobuf___descriptor___Descriptor = ...
    serial_number: typing___Text = ...
    controller_code: typing___Text = ...
    accountid: builtin___int = ...
    appidorname: typing___Text = ...
    controller_type: builtin___int = ...
    only_for_this_serial: builtin___bool = ...

    def __init__(self,
        *,
        serial_number : typing___Optional[typing___Text] = None,
        controller_code : typing___Optional[typing___Text] = None,
        accountid : typing___Optional[builtin___int] = None,
        appidorname : typing___Optional[typing___Text] = None,
        controller_type : typing___Optional[builtin___int] = None,
        only_for_this_serial : typing___Optional[builtin___bool] = None,
        ) -> None: ...
    def HasField(self, field_name: typing_extensions___Literal[u"accountid",b"accountid",u"appidorname",b"appidorname",u"controller_code",b"controller_code",u"controller_type",b"controller_type",u"only_for_this_serial",b"only_for_this_serial",u"serial_number",b"serial_number"]) -> builtin___bool: ...
    def ClearField(self, field_name: typing_extensions___Literal[u"accountid",b"accountid",u"appidorname",b"appidorname",u"controller_code",b"controller_code",u"controller_type",b"controller_type",u"only_for_this_serial",b"only_for_this_serial",u"serial_number",b"serial_number"]) -> None: ...
type___CPhysicalGoods_SteamControllerGetConfig_Request = CPhysicalGoods_SteamControllerGetConfig_Request

class CPhysicalGoods_SteamControllerGetConfig_ControllerConfig(google___protobuf___message___Message):
    DESCRIPTOR: google___protobuf___descriptor___Descriptor = ...
    appidorname: typing___Text = ...
    publishedfileid: builtin___int = ...
    templatename: typing___Text = ...
    serial_number: typing___Text = ...

    def __init__(self,
        *,
        appidorname : typing___Optional[typing___Text] = None,
        publishedfileid : typing___Optional[builtin___int] = None,
        templatename : typing___Optional[typing___Text] = None,
        serial_number : typing___Optional[typing___Text] = None,
        ) -> None: ...
    def HasField(self, field_name: typing_extensions___Literal[u"appidorname",b"appidorname",u"publishedfileid",b"publishedfileid",u"serial_number",b"serial_number",u"templatename",b"templatename"]) -> builtin___bool: ...
    def ClearField(self, field_name: typing_extensions___Literal[u"appidorname",b"appidorname",u"publishedfileid",b"publishedfileid",u"serial_number",b"serial_number",u"templatename",b"templatename"]) -> None: ...
type___CPhysicalGoods_SteamControllerGetConfig_ControllerConfig = CPhysicalGoods_SteamControllerGetConfig_ControllerConfig

class CPhysicalGoods_SteamControllerGetConfig_Response(google___protobuf___message___Message):
    DESCRIPTOR: google___protobuf___descriptor___Descriptor = ...

    @property
    def configurations(self) -> google___protobuf___internal___containers___RepeatedCompositeFieldContainer[type___CPhysicalGoods_SteamControllerGetConfig_ControllerConfig]: ...

    def __init__(self,
        *,
        configurations : typing___Optional[typing___Iterable[type___CPhysicalGoods_SteamControllerGetConfig_ControllerConfig]] = None,
        ) -> None: ...
    def ClearField(self, field_name: typing_extensions___Literal[u"configurations",b"configurations"]) -> None: ...
type___CPhysicalGoods_SteamControllerGetConfig_Response = CPhysicalGoods_SteamControllerGetConfig_Response

class CPhysicalGoods_DeRegisterSteamController_Request(google___protobuf___message___Message):
    DESCRIPTOR: google___protobuf___descriptor___Descriptor = ...
    serial_number: typing___Text = ...
    controller_code: typing___Text = ...
    accountid: builtin___int = ...

    def __init__(self,
        *,
        serial_number : typing___Optional[typing___Text] = None,
        controller_code : typing___Optional[typing___Text] = None,
        accountid : typing___Optional[builtin___int] = None,
        ) -> None: ...
    def HasField(self, field_name: typing_extensions___Literal[u"accountid",b"accountid",u"controller_code",b"controller_code",u"serial_number",b"serial_number"]) -> builtin___bool: ...
    def ClearField(self, field_name: typing_extensions___Literal[u"accountid",b"accountid",u"controller_code",b"controller_code",u"serial_number",b"serial_number"]) -> None: ...
type___CPhysicalGoods_DeRegisterSteamController_Request = CPhysicalGoods_DeRegisterSteamController_Request

class CPhysicalGoods_DeRegisterSteamController_Response(google___protobuf___message___Message):
    DESCRIPTOR: google___protobuf___descriptor___Descriptor = ...

    def __init__(self,
        ) -> None: ...
type___CPhysicalGoods_DeRegisterSteamController_Response = CPhysicalGoods_DeRegisterSteamController_Response

class CPhysicalGoods_SetPersonalizationFile_Request(google___protobuf___message___Message):
    DESCRIPTOR: google___protobuf___descriptor___Descriptor = ...
    serial_number: typing___Text = ...
    publishedfileid: builtin___int = ...
    accountid: builtin___int = ...

    def __init__(self,
        *,
        serial_number : typing___Optional[typing___Text] = None,
        publishedfileid : typing___Optional[builtin___int] = None,
        accountid : typing___Optional[builtin___int] = None,
        ) -> None: ...
    def HasField(self, field_name: typing_extensions___Literal[u"accountid",b"accountid",u"publishedfileid",b"publishedfileid",u"serial_number",b"serial_number"]) -> builtin___bool: ...
    def ClearField(self, field_name: typing_extensions___Literal[u"accountid",b"accountid",u"publishedfileid",b"publishedfileid",u"serial_number",b"serial_number"]) -> None: ...
type___CPhysicalGoods_SetPersonalizationFile_Request = CPhysicalGoods_SetPersonalizationFile_Request

class CPhysicalGoods_SetPersonalizationFile_Response(google___protobuf___message___Message):
    DESCRIPTOR: google___protobuf___descriptor___Descriptor = ...

    def __init__(self,
        ) -> None: ...
type___CPhysicalGoods_SetPersonalizationFile_Response = CPhysicalGoods_SetPersonalizationFile_Response

class CPhysicalGoods_GetPersonalizationFile_Request(google___protobuf___message___Message):
    DESCRIPTOR: google___protobuf___descriptor___Descriptor = ...
    serial_number: typing___Text = ...
    accountid: builtin___int = ...

    def __init__(self,
        *,
        serial_number : typing___Optional[typing___Text] = None,
        accountid : typing___Optional[builtin___int] = None,
        ) -> None: ...
    def HasField(self, field_name: typing_extensions___Literal[u"accountid",b"accountid",u"serial_number",b"serial_number"]) -> builtin___bool: ...
    def ClearField(self, field_name: typing_extensions___Literal[u"accountid",b"accountid",u"serial_number",b"serial_number"]) -> None: ...
type___CPhysicalGoods_GetPersonalizationFile_Request = CPhysicalGoods_GetPersonalizationFile_Request

class CPhysicalGoods_GetPersonalizationFile_Response(google___protobuf___message___Message):
    DESCRIPTOR: google___protobuf___descriptor___Descriptor = ...
    publishedfileid: builtin___int = ...

    def __init__(self,
        *,
        publishedfileid : typing___Optional[builtin___int] = None,
        ) -> None: ...
    def HasField(self, field_name: typing_extensions___Literal[u"publishedfileid",b"publishedfileid"]) -> builtin___bool: ...
    def ClearField(self, field_name: typing_extensions___Literal[u"publishedfileid",b"publishedfileid"]) -> None: ...
type___CPhysicalGoods_GetPersonalizationFile_Response = CPhysicalGoods_GetPersonalizationFile_Response

class PhysicalGoods(google___protobuf___service___Service, metaclass=abc___ABCMeta):
    @abc___abstractmethod
    def RegisterSteamController(self,
        rpc_controller: google___protobuf___service___RpcController,
        request: type___CPhysicalGoods_RegisterSteamController_Request,
        done: typing___Optional[typing___Callable[[type___CPhysicalGoods_RegisterSteamController_Response], None]],
    ) -> concurrent___futures___Future[type___CPhysicalGoods_RegisterSteamController_Response]: ...
    @abc___abstractmethod
    def CompleteSteamControllerRegistration(self,
        rpc_controller: google___protobuf___service___RpcController,
        request: type___CPhysicalGoods_CompleteSteamControllerRegistration_Request,
        done: typing___Optional[typing___Callable[[type___CPhysicalGoods_CompleteSteamControllerRegistration_Response], None]],
    ) -> concurrent___futures___Future[type___CPhysicalGoods_CompleteSteamControllerRegistration_Response]: ...
    @abc___abstractmethod
    def QueryAccountsRegisteredToController(self,
        rpc_controller: google___protobuf___service___RpcController,
        request: type___CPhysicalGoods_QueryAccountsRegisteredToSerial_Request,
        done: typing___Optional[typing___Callable[[type___CPhysicalGoods_QueryAccountsRegisteredToSerial_Response], None]],
    ) -> concurrent___futures___Future[type___CPhysicalGoods_QueryAccountsRegisteredToSerial_Response]: ...
    @abc___abstractmethod
    def SetDesiredControllerConfigForApp(self,
        rpc_controller: google___protobuf___service___RpcController,
        request: type___CPhysicalGoods_SteamControllerSetConfig_Request,
        done: typing___Optional[typing___Callable[[type___CPhysicalGoods_SteamControllerSetConfig_Response], None]],
    ) -> concurrent___futures___Future[type___CPhysicalGoods_SteamControllerSetConfig_Response]: ...
    @abc___abstractmethod
    def GetDesiredControllerConfigForApp(self,
        rpc_controller: google___protobuf___service___RpcController,
        request: type___CPhysicalGoods_SteamControllerGetConfig_Request,
        done: typing___Optional[typing___Callable[[type___CPhysicalGoods_SteamControllerGetConfig_Response], None]],
    ) -> concurrent___futures___Future[type___CPhysicalGoods_SteamControllerGetConfig_Response]: ...
    @abc___abstractmethod
    def DeRegisterSteamController(self,
        rpc_controller: google___protobuf___service___RpcController,
        request: type___CPhysicalGoods_DeRegisterSteamController_Request,
        done: typing___Optional[typing___Callable[[type___CPhysicalGoods_DeRegisterSteamController_Response], None]],
    ) -> concurrent___futures___Future[type___CPhysicalGoods_DeRegisterSteamController_Response]: ...
    @abc___abstractmethod
    def SetControllerPersonalizationFile(self,
        rpc_controller: google___protobuf___service___RpcController,
        request: type___CPhysicalGoods_SetPersonalizationFile_Request,
        done: typing___Optional[typing___Callable[[type___CPhysicalGoods_SetPersonalizationFile_Response], None]],
    ) -> concurrent___futures___Future[type___CPhysicalGoods_SetPersonalizationFile_Response]: ...
    @abc___abstractmethod
    def GetControllerPersonalizationFile(self,
        rpc_controller: google___protobuf___service___RpcController,
        request: type___CPhysicalGoods_GetPersonalizationFile_Request,
        done: typing___Optional[typing___Callable[[type___CPhysicalGoods_GetPersonalizationFile_Response], None]],
    ) -> concurrent___futures___Future[type___CPhysicalGoods_GetPersonalizationFile_Response]: ...
class PhysicalGoods_Stub(PhysicalGoods):
    def __init__(self, rpc_channel: google___protobuf___service___RpcChannel) -> None: ...
    def RegisterSteamController(self,
        rpc_controller: google___protobuf___service___RpcController,
        request: type___CPhysicalGoods_RegisterSteamController_Request,
        done: typing___Optional[typing___Callable[[type___CPhysicalGoods_RegisterSteamController_Response], None]],
    ) -> concurrent___futures___Future[type___CPhysicalGoods_RegisterSteamController_Response]: ...
    def CompleteSteamControllerRegistration(self,
        rpc_controller: google___protobuf___service___RpcController,
        request: type___CPhysicalGoods_CompleteSteamControllerRegistration_Request,
        done: typing___Optional[typing___Callable[[type___CPhysicalGoods_CompleteSteamControllerRegistration_Response], None]],
    ) -> concurrent___futures___Future[type___CPhysicalGoods_CompleteSteamControllerRegistration_Response]: ...
    def QueryAccountsRegisteredToController(self,
        rpc_controller: google___protobuf___service___RpcController,
        request: type___CPhysicalGoods_QueryAccountsRegisteredToSerial_Request,
        done: typing___Optional[typing___Callable[[type___CPhysicalGoods_QueryAccountsRegisteredToSerial_Response], None]],
    ) -> concurrent___futures___Future[type___CPhysicalGoods_QueryAccountsRegisteredToSerial_Response]: ...
    def SetDesiredControllerConfigForApp(self,
        rpc_controller: google___protobuf___service___RpcController,
        request: type___CPhysicalGoods_SteamControllerSetConfig_Request,
        done: typing___Optional[typing___Callable[[type___CPhysicalGoods_SteamControllerSetConfig_Response], None]],
    ) -> concurrent___futures___Future[type___CPhysicalGoods_SteamControllerSetConfig_Response]: ...
    def GetDesiredControllerConfigForApp(self,
        rpc_controller: google___protobuf___service___RpcController,
        request: type___CPhysicalGoods_SteamControllerGetConfig_Request,
        done: typing___Optional[typing___Callable[[type___CPhysicalGoods_SteamControllerGetConfig_Response], None]],
    ) -> concurrent___futures___Future[type___CPhysicalGoods_SteamControllerGetConfig_Response]: ...
    def DeRegisterSteamController(self,
        rpc_controller: google___protobuf___service___RpcController,
        request: type___CPhysicalGoods_DeRegisterSteamController_Request,
        done: typing___Optional[typing___Callable[[type___CPhysicalGoods_DeRegisterSteamController_Response], None]],
    ) -> concurrent___futures___Future[type___CPhysicalGoods_DeRegisterSteamController_Response]: ...
    def SetControllerPersonalizationFile(self,
        rpc_controller: google___protobuf___service___RpcController,
        request: type___CPhysicalGoods_SetPersonalizationFile_Request,
        done: typing___Optional[typing___Callable[[type___CPhysicalGoods_SetPersonalizationFile_Response], None]],
    ) -> concurrent___futures___Future[type___CPhysicalGoods_SetPersonalizationFile_Response]: ...
    def GetControllerPersonalizationFile(self,
        rpc_controller: google___protobuf___service___RpcController,
        request: type___CPhysicalGoods_GetPersonalizationFile_Request,
        done: typing___Optional[typing___Callable[[type___CPhysicalGoods_GetPersonalizationFile_Response], None]],
    ) -> concurrent___futures___Future[type___CPhysicalGoods_GetPersonalizationFile_Response]: ...