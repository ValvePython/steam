# Change notes

## 1.0.0

This release brings some breaking changes

- Removed imports from 'steam' namespace
- Replaced builtin CM server list with automatic discovery via WebAPI or DNS
- Removed `SteamClient.unifed_messages`
- UM/ServiceMethods are now handled in the `SteamClient` instance. See `SteamClient.send_um()`
- Removed `steam.client.mixins` package
- Renamed `medium` param to `backend` on `SteamAuthenticator`
- Added `WebAuth.cli_login()`, handles all steps of the login process
- Made `password` param optional on `WebAuth`
- Replaced `cryptography` library with `pycryptodomex`
- Added `rich_presence` property to `SteamUser`
- Fixed `create_emergency_codes()` not returning codes
- Fixed `validate_phone_number()` returning no data
- Updated protobufs
- Removed `SteamClient.change_email()`
- Removed `SteamClient.create_account()`
- `get_product_info()` now replaces invalid unicode chars
- Updated `SteamID.is_valid`
- Updated various Enums
- Updated EMsg Enum
- Messages now have a payload property set when the body cannot be parsed
- Updated protocol version to 65580
- Added `CDNClient`
