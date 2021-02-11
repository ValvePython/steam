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
    EnumDescriptor as google___protobuf___descriptor___EnumDescriptor,
    FileDescriptor as google___protobuf___descriptor___FileDescriptor,
)

from google.protobuf.internal.enum_type_wrapper import (
    _EnumTypeWrapper as google___protobuf___internal___enum_type_wrapper____EnumTypeWrapper,
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
    NewType as typing___NewType,
    Optional as typing___Optional,
    Text as typing___Text,
    cast as typing___cast,
)

from typing_extensions import (
    Literal as typing_extensions___Literal,
)


builtin___bool = bool
builtin___bytes = bytes
builtin___float = float
builtin___int = int


DESCRIPTOR: google___protobuf___descriptor___FileDescriptor = ...

EKeyEscrowUsageValue = typing___NewType('EKeyEscrowUsageValue', builtin___int)
type___EKeyEscrowUsageValue = EKeyEscrowUsageValue
EKeyEscrowUsage: _EKeyEscrowUsage
class _EKeyEscrowUsage(google___protobuf___internal___enum_type_wrapper____EnumTypeWrapper[EKeyEscrowUsageValue]):
    DESCRIPTOR: google___protobuf___descriptor___EnumDescriptor = ...
    k_EKeyEscrowUsageStreamingDevice = typing___cast(EKeyEscrowUsageValue, 0)
k_EKeyEscrowUsageStreamingDevice = typing___cast(EKeyEscrowUsageValue, 0)
type___EKeyEscrowUsage = EKeyEscrowUsage

class CKeyEscrow_Request(google___protobuf___message___Message):
    DESCRIPTOR: google___protobuf___descriptor___Descriptor = ...
    rsa_oaep_sha_ticket: builtin___bytes = ...
    password: builtin___bytes = ...
    usage: type___EKeyEscrowUsageValue = ...
    device_name: typing___Text = ...

    def __init__(self,
        *,
        rsa_oaep_sha_ticket : typing___Optional[builtin___bytes] = None,
        password : typing___Optional[builtin___bytes] = None,
        usage : typing___Optional[type___EKeyEscrowUsageValue] = None,
        device_name : typing___Optional[typing___Text] = None,
        ) -> None: ...
    def HasField(self, field_name: typing_extensions___Literal[u"device_name",b"device_name",u"password",b"password",u"rsa_oaep_sha_ticket",b"rsa_oaep_sha_ticket",u"usage",b"usage"]) -> builtin___bool: ...
    def ClearField(self, field_name: typing_extensions___Literal[u"device_name",b"device_name",u"password",b"password",u"rsa_oaep_sha_ticket",b"rsa_oaep_sha_ticket",u"usage",b"usage"]) -> None: ...
type___CKeyEscrow_Request = CKeyEscrow_Request

class CKeyEscrow_Ticket(google___protobuf___message___Message):
    DESCRIPTOR: google___protobuf___descriptor___Descriptor = ...
    password: builtin___bytes = ...
    identifier: builtin___int = ...
    payload: builtin___bytes = ...
    timestamp: builtin___int = ...
    usage: type___EKeyEscrowUsageValue = ...
    device_name: typing___Text = ...
    device_model: typing___Text = ...
    device_serial: typing___Text = ...
    device_provisioning_id: builtin___int = ...

    def __init__(self,
        *,
        password : typing___Optional[builtin___bytes] = None,
        identifier : typing___Optional[builtin___int] = None,
        payload : typing___Optional[builtin___bytes] = None,
        timestamp : typing___Optional[builtin___int] = None,
        usage : typing___Optional[type___EKeyEscrowUsageValue] = None,
        device_name : typing___Optional[typing___Text] = None,
        device_model : typing___Optional[typing___Text] = None,
        device_serial : typing___Optional[typing___Text] = None,
        device_provisioning_id : typing___Optional[builtin___int] = None,
        ) -> None: ...
    def HasField(self, field_name: typing_extensions___Literal[u"device_model",b"device_model",u"device_name",b"device_name",u"device_provisioning_id",b"device_provisioning_id",u"device_serial",b"device_serial",u"identifier",b"identifier",u"password",b"password",u"payload",b"payload",u"timestamp",b"timestamp",u"usage",b"usage"]) -> builtin___bool: ...
    def ClearField(self, field_name: typing_extensions___Literal[u"device_model",b"device_model",u"device_name",b"device_name",u"device_provisioning_id",b"device_provisioning_id",u"device_serial",b"device_serial",u"identifier",b"identifier",u"password",b"password",u"payload",b"payload",u"timestamp",b"timestamp",u"usage",b"usage"]) -> None: ...
type___CKeyEscrow_Ticket = CKeyEscrow_Ticket

class CKeyEscrow_Response(google___protobuf___message___Message):
    DESCRIPTOR: google___protobuf___descriptor___Descriptor = ...

    @property
    def ticket(self) -> type___CKeyEscrow_Ticket: ...

    def __init__(self,
        *,
        ticket : typing___Optional[type___CKeyEscrow_Ticket] = None,
        ) -> None: ...
    def HasField(self, field_name: typing_extensions___Literal[u"ticket",b"ticket"]) -> builtin___bool: ...
    def ClearField(self, field_name: typing_extensions___Literal[u"ticket",b"ticket"]) -> None: ...
type___CKeyEscrow_Response = CKeyEscrow_Response

class Secrets(google___protobuf___service___Service, metaclass=abc___ABCMeta):
    @abc___abstractmethod
    def KeyEscrow(self,
        rpc_controller: google___protobuf___service___RpcController,
        request: type___CKeyEscrow_Request,
        done: typing___Optional[typing___Callable[[type___CKeyEscrow_Response], None]],
    ) -> concurrent___futures___Future[type___CKeyEscrow_Response]: ...
class Secrets_Stub(Secrets):
    def __init__(self, rpc_channel: google___protobuf___service___RpcChannel) -> None: ...
    def KeyEscrow(self,
        rpc_controller: google___protobuf___service___RpcController,
        request: type___CKeyEscrow_Request,
        done: typing___Optional[typing___Callable[[type___CKeyEscrow_Response], None]],
    ) -> concurrent___futures___Future[type___CKeyEscrow_Response]: ...