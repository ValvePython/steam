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
    RepeatedScalarFieldContainer as google___protobuf___internal___containers___RepeatedScalarFieldContainer,
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

class CTwoFactor_Status_Request(google___protobuf___message___Message):
    DESCRIPTOR: google___protobuf___descriptor___Descriptor = ...
    steamid: builtin___int = ...

    def __init__(self,
        *,
        steamid : typing___Optional[builtin___int] = None,
        ) -> None: ...
    def HasField(self, field_name: typing_extensions___Literal[u"steamid",b"steamid"]) -> builtin___bool: ...
    def ClearField(self, field_name: typing_extensions___Literal[u"steamid",b"steamid"]) -> None: ...
type___CTwoFactor_Status_Request = CTwoFactor_Status_Request

class CTwoFactor_Status_Response(google___protobuf___message___Message):
    DESCRIPTOR: google___protobuf___descriptor___Descriptor = ...
    state: builtin___int = ...
    inactivation_reason: builtin___int = ...
    authenticator_type: builtin___int = ...
    authenticator_allowed: builtin___bool = ...
    steamguard_scheme: builtin___int = ...
    token_gid: typing___Text = ...
    email_validated: builtin___bool = ...
    device_identifier: typing___Text = ...
    time_created: builtin___int = ...
    revocation_attempts_remaining: builtin___int = ...
    classified_agent: typing___Text = ...
    allow_external_authenticator: builtin___bool = ...
    time_transferred: builtin___int = ...

    def __init__(self,
        *,
        state : typing___Optional[builtin___int] = None,
        inactivation_reason : typing___Optional[builtin___int] = None,
        authenticator_type : typing___Optional[builtin___int] = None,
        authenticator_allowed : typing___Optional[builtin___bool] = None,
        steamguard_scheme : typing___Optional[builtin___int] = None,
        token_gid : typing___Optional[typing___Text] = None,
        email_validated : typing___Optional[builtin___bool] = None,
        device_identifier : typing___Optional[typing___Text] = None,
        time_created : typing___Optional[builtin___int] = None,
        revocation_attempts_remaining : typing___Optional[builtin___int] = None,
        classified_agent : typing___Optional[typing___Text] = None,
        allow_external_authenticator : typing___Optional[builtin___bool] = None,
        time_transferred : typing___Optional[builtin___int] = None,
        ) -> None: ...
    def HasField(self, field_name: typing_extensions___Literal[u"allow_external_authenticator",b"allow_external_authenticator",u"authenticator_allowed",b"authenticator_allowed",u"authenticator_type",b"authenticator_type",u"classified_agent",b"classified_agent",u"device_identifier",b"device_identifier",u"email_validated",b"email_validated",u"inactivation_reason",b"inactivation_reason",u"revocation_attempts_remaining",b"revocation_attempts_remaining",u"state",b"state",u"steamguard_scheme",b"steamguard_scheme",u"time_created",b"time_created",u"time_transferred",b"time_transferred",u"token_gid",b"token_gid"]) -> builtin___bool: ...
    def ClearField(self, field_name: typing_extensions___Literal[u"allow_external_authenticator",b"allow_external_authenticator",u"authenticator_allowed",b"authenticator_allowed",u"authenticator_type",b"authenticator_type",u"classified_agent",b"classified_agent",u"device_identifier",b"device_identifier",u"email_validated",b"email_validated",u"inactivation_reason",b"inactivation_reason",u"revocation_attempts_remaining",b"revocation_attempts_remaining",u"state",b"state",u"steamguard_scheme",b"steamguard_scheme",u"time_created",b"time_created",u"time_transferred",b"time_transferred",u"token_gid",b"token_gid"]) -> None: ...
type___CTwoFactor_Status_Response = CTwoFactor_Status_Response

class CTwoFactor_AddAuthenticator_Request(google___protobuf___message___Message):
    DESCRIPTOR: google___protobuf___descriptor___Descriptor = ...
    steamid: builtin___int = ...
    authenticator_time: builtin___int = ...
    serial_number: builtin___int = ...
    authenticator_type: builtin___int = ...
    device_identifier: typing___Text = ...
    sms_phone_id: typing___Text = ...
    http_headers: google___protobuf___internal___containers___RepeatedScalarFieldContainer[typing___Text] = ...

    def __init__(self,
        *,
        steamid : typing___Optional[builtin___int] = None,
        authenticator_time : typing___Optional[builtin___int] = None,
        serial_number : typing___Optional[builtin___int] = None,
        authenticator_type : typing___Optional[builtin___int] = None,
        device_identifier : typing___Optional[typing___Text] = None,
        sms_phone_id : typing___Optional[typing___Text] = None,
        http_headers : typing___Optional[typing___Iterable[typing___Text]] = None,
        ) -> None: ...
    def HasField(self, field_name: typing_extensions___Literal[u"authenticator_time",b"authenticator_time",u"authenticator_type",b"authenticator_type",u"device_identifier",b"device_identifier",u"serial_number",b"serial_number",u"sms_phone_id",b"sms_phone_id",u"steamid",b"steamid"]) -> builtin___bool: ...
    def ClearField(self, field_name: typing_extensions___Literal[u"authenticator_time",b"authenticator_time",u"authenticator_type",b"authenticator_type",u"device_identifier",b"device_identifier",u"http_headers",b"http_headers",u"serial_number",b"serial_number",u"sms_phone_id",b"sms_phone_id",u"steamid",b"steamid"]) -> None: ...
type___CTwoFactor_AddAuthenticator_Request = CTwoFactor_AddAuthenticator_Request

class CTwoFactor_AddAuthenticator_Response(google___protobuf___message___Message):
    DESCRIPTOR: google___protobuf___descriptor___Descriptor = ...
    shared_secret: builtin___bytes = ...
    serial_number: builtin___int = ...
    revocation_code: typing___Text = ...
    uri: typing___Text = ...
    server_time: builtin___int = ...
    account_name: typing___Text = ...
    token_gid: typing___Text = ...
    identity_secret: builtin___bytes = ...
    secret_1: builtin___bytes = ...
    status: builtin___int = ...

    def __init__(self,
        *,
        shared_secret : typing___Optional[builtin___bytes] = None,
        serial_number : typing___Optional[builtin___int] = None,
        revocation_code : typing___Optional[typing___Text] = None,
        uri : typing___Optional[typing___Text] = None,
        server_time : typing___Optional[builtin___int] = None,
        account_name : typing___Optional[typing___Text] = None,
        token_gid : typing___Optional[typing___Text] = None,
        identity_secret : typing___Optional[builtin___bytes] = None,
        secret_1 : typing___Optional[builtin___bytes] = None,
        status : typing___Optional[builtin___int] = None,
        ) -> None: ...
    def HasField(self, field_name: typing_extensions___Literal[u"account_name",b"account_name",u"identity_secret",b"identity_secret",u"revocation_code",b"revocation_code",u"secret_1",b"secret_1",u"serial_number",b"serial_number",u"server_time",b"server_time",u"shared_secret",b"shared_secret",u"status",b"status",u"token_gid",b"token_gid",u"uri",b"uri"]) -> builtin___bool: ...
    def ClearField(self, field_name: typing_extensions___Literal[u"account_name",b"account_name",u"identity_secret",b"identity_secret",u"revocation_code",b"revocation_code",u"secret_1",b"secret_1",u"serial_number",b"serial_number",u"server_time",b"server_time",u"shared_secret",b"shared_secret",u"status",b"status",u"token_gid",b"token_gid",u"uri",b"uri"]) -> None: ...
type___CTwoFactor_AddAuthenticator_Response = CTwoFactor_AddAuthenticator_Response

class CTwoFactor_SendEmail_Request(google___protobuf___message___Message):
    DESCRIPTOR: google___protobuf___descriptor___Descriptor = ...
    steamid: builtin___int = ...
    email_type: builtin___int = ...
    include_activation_code: builtin___bool = ...

    def __init__(self,
        *,
        steamid : typing___Optional[builtin___int] = None,
        email_type : typing___Optional[builtin___int] = None,
        include_activation_code : typing___Optional[builtin___bool] = None,
        ) -> None: ...
    def HasField(self, field_name: typing_extensions___Literal[u"email_type",b"email_type",u"include_activation_code",b"include_activation_code",u"steamid",b"steamid"]) -> builtin___bool: ...
    def ClearField(self, field_name: typing_extensions___Literal[u"email_type",b"email_type",u"include_activation_code",b"include_activation_code",u"steamid",b"steamid"]) -> None: ...
type___CTwoFactor_SendEmail_Request = CTwoFactor_SendEmail_Request

class CTwoFactor_SendEmail_Response(google___protobuf___message___Message):
    DESCRIPTOR: google___protobuf___descriptor___Descriptor = ...

    def __init__(self,
        ) -> None: ...
type___CTwoFactor_SendEmail_Response = CTwoFactor_SendEmail_Response

class CTwoFactor_FinalizeAddAuthenticator_Request(google___protobuf___message___Message):
    DESCRIPTOR: google___protobuf___descriptor___Descriptor = ...
    steamid: builtin___int = ...
    authenticator_code: typing___Text = ...
    authenticator_time: builtin___int = ...
    activation_code: typing___Text = ...
    http_headers: google___protobuf___internal___containers___RepeatedScalarFieldContainer[typing___Text] = ...

    def __init__(self,
        *,
        steamid : typing___Optional[builtin___int] = None,
        authenticator_code : typing___Optional[typing___Text] = None,
        authenticator_time : typing___Optional[builtin___int] = None,
        activation_code : typing___Optional[typing___Text] = None,
        http_headers : typing___Optional[typing___Iterable[typing___Text]] = None,
        ) -> None: ...
    def HasField(self, field_name: typing_extensions___Literal[u"activation_code",b"activation_code",u"authenticator_code",b"authenticator_code",u"authenticator_time",b"authenticator_time",u"steamid",b"steamid"]) -> builtin___bool: ...
    def ClearField(self, field_name: typing_extensions___Literal[u"activation_code",b"activation_code",u"authenticator_code",b"authenticator_code",u"authenticator_time",b"authenticator_time",u"http_headers",b"http_headers",u"steamid",b"steamid"]) -> None: ...
type___CTwoFactor_FinalizeAddAuthenticator_Request = CTwoFactor_FinalizeAddAuthenticator_Request

class CTwoFactor_FinalizeAddAuthenticator_Response(google___protobuf___message___Message):
    DESCRIPTOR: google___protobuf___descriptor___Descriptor = ...
    success: builtin___bool = ...
    want_more: builtin___bool = ...
    server_time: builtin___int = ...
    status: builtin___int = ...

    def __init__(self,
        *,
        success : typing___Optional[builtin___bool] = None,
        want_more : typing___Optional[builtin___bool] = None,
        server_time : typing___Optional[builtin___int] = None,
        status : typing___Optional[builtin___int] = None,
        ) -> None: ...
    def HasField(self, field_name: typing_extensions___Literal[u"server_time",b"server_time",u"status",b"status",u"success",b"success",u"want_more",b"want_more"]) -> builtin___bool: ...
    def ClearField(self, field_name: typing_extensions___Literal[u"server_time",b"server_time",u"status",b"status",u"success",b"success",u"want_more",b"want_more"]) -> None: ...
type___CTwoFactor_FinalizeAddAuthenticator_Response = CTwoFactor_FinalizeAddAuthenticator_Response

class CTwoFactor_RemoveAuthenticator_Request(google___protobuf___message___Message):
    DESCRIPTOR: google___protobuf___descriptor___Descriptor = ...
    revocation_code: typing___Text = ...
    revocation_reason: builtin___int = ...
    steamguard_scheme: builtin___int = ...
    remove_all_steamguard_cookies: builtin___bool = ...

    def __init__(self,
        *,
        revocation_code : typing___Optional[typing___Text] = None,
        revocation_reason : typing___Optional[builtin___int] = None,
        steamguard_scheme : typing___Optional[builtin___int] = None,
        remove_all_steamguard_cookies : typing___Optional[builtin___bool] = None,
        ) -> None: ...
    def HasField(self, field_name: typing_extensions___Literal[u"remove_all_steamguard_cookies",b"remove_all_steamguard_cookies",u"revocation_code",b"revocation_code",u"revocation_reason",b"revocation_reason",u"steamguard_scheme",b"steamguard_scheme"]) -> builtin___bool: ...
    def ClearField(self, field_name: typing_extensions___Literal[u"remove_all_steamguard_cookies",b"remove_all_steamguard_cookies",u"revocation_code",b"revocation_code",u"revocation_reason",b"revocation_reason",u"steamguard_scheme",b"steamguard_scheme"]) -> None: ...
type___CTwoFactor_RemoveAuthenticator_Request = CTwoFactor_RemoveAuthenticator_Request

class CTwoFactor_RemoveAuthenticator_Response(google___protobuf___message___Message):
    DESCRIPTOR: google___protobuf___descriptor___Descriptor = ...
    success: builtin___bool = ...
    server_time: builtin___int = ...
    revocation_attempts_remaining: builtin___int = ...

    def __init__(self,
        *,
        success : typing___Optional[builtin___bool] = None,
        server_time : typing___Optional[builtin___int] = None,
        revocation_attempts_remaining : typing___Optional[builtin___int] = None,
        ) -> None: ...
    def HasField(self, field_name: typing_extensions___Literal[u"revocation_attempts_remaining",b"revocation_attempts_remaining",u"server_time",b"server_time",u"success",b"success"]) -> builtin___bool: ...
    def ClearField(self, field_name: typing_extensions___Literal[u"revocation_attempts_remaining",b"revocation_attempts_remaining",u"server_time",b"server_time",u"success",b"success"]) -> None: ...
type___CTwoFactor_RemoveAuthenticator_Response = CTwoFactor_RemoveAuthenticator_Response

class CTwoFactor_CreateEmergencyCodes_Request(google___protobuf___message___Message):
    DESCRIPTOR: google___protobuf___descriptor___Descriptor = ...
    code: typing___Text = ...

    def __init__(self,
        *,
        code : typing___Optional[typing___Text] = None,
        ) -> None: ...
    def HasField(self, field_name: typing_extensions___Literal[u"code",b"code"]) -> builtin___bool: ...
    def ClearField(self, field_name: typing_extensions___Literal[u"code",b"code"]) -> None: ...
type___CTwoFactor_CreateEmergencyCodes_Request = CTwoFactor_CreateEmergencyCodes_Request

class CTwoFactor_CreateEmergencyCodes_Response(google___protobuf___message___Message):
    DESCRIPTOR: google___protobuf___descriptor___Descriptor = ...
    codes: google___protobuf___internal___containers___RepeatedScalarFieldContainer[typing___Text] = ...

    def __init__(self,
        *,
        codes : typing___Optional[typing___Iterable[typing___Text]] = None,
        ) -> None: ...
    def ClearField(self, field_name: typing_extensions___Literal[u"codes",b"codes"]) -> None: ...
type___CTwoFactor_CreateEmergencyCodes_Response = CTwoFactor_CreateEmergencyCodes_Response

class CTwoFactor_DestroyEmergencyCodes_Request(google___protobuf___message___Message):
    DESCRIPTOR: google___protobuf___descriptor___Descriptor = ...
    steamid: builtin___int = ...

    def __init__(self,
        *,
        steamid : typing___Optional[builtin___int] = None,
        ) -> None: ...
    def HasField(self, field_name: typing_extensions___Literal[u"steamid",b"steamid"]) -> builtin___bool: ...
    def ClearField(self, field_name: typing_extensions___Literal[u"steamid",b"steamid"]) -> None: ...
type___CTwoFactor_DestroyEmergencyCodes_Request = CTwoFactor_DestroyEmergencyCodes_Request

class CTwoFactor_DestroyEmergencyCodes_Response(google___protobuf___message___Message):
    DESCRIPTOR: google___protobuf___descriptor___Descriptor = ...

    def __init__(self,
        ) -> None: ...
type___CTwoFactor_DestroyEmergencyCodes_Response = CTwoFactor_DestroyEmergencyCodes_Response

class CTwoFactor_ValidateToken_Request(google___protobuf___message___Message):
    DESCRIPTOR: google___protobuf___descriptor___Descriptor = ...
    code: typing___Text = ...

    def __init__(self,
        *,
        code : typing___Optional[typing___Text] = None,
        ) -> None: ...
    def HasField(self, field_name: typing_extensions___Literal[u"code",b"code"]) -> builtin___bool: ...
    def ClearField(self, field_name: typing_extensions___Literal[u"code",b"code"]) -> None: ...
type___CTwoFactor_ValidateToken_Request = CTwoFactor_ValidateToken_Request

class CTwoFactor_ValidateToken_Response(google___protobuf___message___Message):
    DESCRIPTOR: google___protobuf___descriptor___Descriptor = ...
    valid: builtin___bool = ...

    def __init__(self,
        *,
        valid : typing___Optional[builtin___bool] = None,
        ) -> None: ...
    def HasField(self, field_name: typing_extensions___Literal[u"valid",b"valid"]) -> builtin___bool: ...
    def ClearField(self, field_name: typing_extensions___Literal[u"valid",b"valid"]) -> None: ...
type___CTwoFactor_ValidateToken_Response = CTwoFactor_ValidateToken_Response

class TwoFactor(google___protobuf___service___Service, metaclass=abc___ABCMeta):
    @abc___abstractmethod
    def QueryStatus(self,
        rpc_controller: google___protobuf___service___RpcController,
        request: type___CTwoFactor_Status_Request,
        done: typing___Optional[typing___Callable[[type___CTwoFactor_Status_Response], None]],
    ) -> concurrent___futures___Future[type___CTwoFactor_Status_Response]: ...
    @abc___abstractmethod
    def AddAuthenticator(self,
        rpc_controller: google___protobuf___service___RpcController,
        request: type___CTwoFactor_AddAuthenticator_Request,
        done: typing___Optional[typing___Callable[[type___CTwoFactor_AddAuthenticator_Response], None]],
    ) -> concurrent___futures___Future[type___CTwoFactor_AddAuthenticator_Response]: ...
    @abc___abstractmethod
    def SendEmail(self,
        rpc_controller: google___protobuf___service___RpcController,
        request: type___CTwoFactor_SendEmail_Request,
        done: typing___Optional[typing___Callable[[type___CTwoFactor_SendEmail_Response], None]],
    ) -> concurrent___futures___Future[type___CTwoFactor_SendEmail_Response]: ...
    @abc___abstractmethod
    def FinalizeAddAuthenticator(self,
        rpc_controller: google___protobuf___service___RpcController,
        request: type___CTwoFactor_FinalizeAddAuthenticator_Request,
        done: typing___Optional[typing___Callable[[type___CTwoFactor_FinalizeAddAuthenticator_Response], None]],
    ) -> concurrent___futures___Future[type___CTwoFactor_FinalizeAddAuthenticator_Response]: ...
    @abc___abstractmethod
    def RemoveAuthenticator(self,
        rpc_controller: google___protobuf___service___RpcController,
        request: type___CTwoFactor_RemoveAuthenticator_Request,
        done: typing___Optional[typing___Callable[[type___CTwoFactor_RemoveAuthenticator_Response], None]],
    ) -> concurrent___futures___Future[type___CTwoFactor_RemoveAuthenticator_Response]: ...
    @abc___abstractmethod
    def CreateEmergencyCodes(self,
        rpc_controller: google___protobuf___service___RpcController,
        request: type___CTwoFactor_CreateEmergencyCodes_Request,
        done: typing___Optional[typing___Callable[[type___CTwoFactor_CreateEmergencyCodes_Response], None]],
    ) -> concurrent___futures___Future[type___CTwoFactor_CreateEmergencyCodes_Response]: ...
    @abc___abstractmethod
    def DestroyEmergencyCodes(self,
        rpc_controller: google___protobuf___service___RpcController,
        request: type___CTwoFactor_DestroyEmergencyCodes_Request,
        done: typing___Optional[typing___Callable[[type___CTwoFactor_DestroyEmergencyCodes_Response], None]],
    ) -> concurrent___futures___Future[type___CTwoFactor_DestroyEmergencyCodes_Response]: ...
    @abc___abstractmethod
    def ValidateToken(self,
        rpc_controller: google___protobuf___service___RpcController,
        request: type___CTwoFactor_ValidateToken_Request,
        done: typing___Optional[typing___Callable[[type___CTwoFactor_ValidateToken_Response], None]],
    ) -> concurrent___futures___Future[type___CTwoFactor_ValidateToken_Response]: ...
class TwoFactor_Stub(TwoFactor):
    def __init__(self, rpc_channel: google___protobuf___service___RpcChannel) -> None: ...
    def QueryStatus(self,
        rpc_controller: google___protobuf___service___RpcController,
        request: type___CTwoFactor_Status_Request,
        done: typing___Optional[typing___Callable[[type___CTwoFactor_Status_Response], None]],
    ) -> concurrent___futures___Future[type___CTwoFactor_Status_Response]: ...
    def AddAuthenticator(self,
        rpc_controller: google___protobuf___service___RpcController,
        request: type___CTwoFactor_AddAuthenticator_Request,
        done: typing___Optional[typing___Callable[[type___CTwoFactor_AddAuthenticator_Response], None]],
    ) -> concurrent___futures___Future[type___CTwoFactor_AddAuthenticator_Response]: ...
    def SendEmail(self,
        rpc_controller: google___protobuf___service___RpcController,
        request: type___CTwoFactor_SendEmail_Request,
        done: typing___Optional[typing___Callable[[type___CTwoFactor_SendEmail_Response], None]],
    ) -> concurrent___futures___Future[type___CTwoFactor_SendEmail_Response]: ...
    def FinalizeAddAuthenticator(self,
        rpc_controller: google___protobuf___service___RpcController,
        request: type___CTwoFactor_FinalizeAddAuthenticator_Request,
        done: typing___Optional[typing___Callable[[type___CTwoFactor_FinalizeAddAuthenticator_Response], None]],
    ) -> concurrent___futures___Future[type___CTwoFactor_FinalizeAddAuthenticator_Response]: ...
    def RemoveAuthenticator(self,
        rpc_controller: google___protobuf___service___RpcController,
        request: type___CTwoFactor_RemoveAuthenticator_Request,
        done: typing___Optional[typing___Callable[[type___CTwoFactor_RemoveAuthenticator_Response], None]],
    ) -> concurrent___futures___Future[type___CTwoFactor_RemoveAuthenticator_Response]: ...
    def CreateEmergencyCodes(self,
        rpc_controller: google___protobuf___service___RpcController,
        request: type___CTwoFactor_CreateEmergencyCodes_Request,
        done: typing___Optional[typing___Callable[[type___CTwoFactor_CreateEmergencyCodes_Response], None]],
    ) -> concurrent___futures___Future[type___CTwoFactor_CreateEmergencyCodes_Response]: ...
    def DestroyEmergencyCodes(self,
        rpc_controller: google___protobuf___service___RpcController,
        request: type___CTwoFactor_DestroyEmergencyCodes_Request,
        done: typing___Optional[typing___Callable[[type___CTwoFactor_DestroyEmergencyCodes_Response], None]],
    ) -> concurrent___futures___Future[type___CTwoFactor_DestroyEmergencyCodes_Response]: ...
    def ValidateToken(self,
        rpc_controller: google___protobuf___service___RpcController,
        request: type___CTwoFactor_ValidateToken_Request,
        done: typing___Optional[typing___Callable[[type___CTwoFactor_ValidateToken_Response], None]],
    ) -> concurrent___futures___Future[type___CTwoFactor_ValidateToken_Response]: ...