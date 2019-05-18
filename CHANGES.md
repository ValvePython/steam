# Change notes

## 1.0.0

This release brings some breaking changes

- Replaced builtin CM server list with automatic discovery via WebAPI or DNS
- Removed `steam.client.mixins` package
- Renamed `medium` param to `backend` on `SteamAuthenticator`
- Added `WebAuth.cli_login()`, handles all steps of the login process
- Made `password` param optional on `WebAuth`
- Replaced `cryptography` library with `pycryptodomex`
- Added `rich_presence` property to `SteamUser`
- Fixed `create_emergency_codes()` not returning codes
- Fixed `validate_phone_number()` returning no data
- Added protos for new chat via unified messages
- Updated protobufs
- Removed `SteamClient.change_email()`
- Removed `SteamClient.create_account()`
- `SteanClient.unified_messages` now expose errors by returning a tuple `(result, error)`
- `get_product_info()` now replaces invalid unicode chars
- Updated `SteamID.is_valid`
- Updated various Enums
