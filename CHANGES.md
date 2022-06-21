# Change notes

## 2.0.0

This release brings breaking changes

### steam.client

- Add `steam.monkey` module for applying gevent monkey patches
- Removed monkey patching by default. See `steam.monkey` for details

## 1.0.0

This release brings breaking changes

### General

- Added steam.utils.appcache methods for parsing appcache files
- Replaced `cryptography` library with `pycryptodomex`
- Updated all enums
- Removed imports from 'steam' namespace
- Renamed `steam.util` to `steam.utils`
- Moved proto utils to `steam.utils.proto`
- Moved SteamClient dependecies to `client` extras

### steam.steamid

- Added support for invite codes in SteamID
- Updated `SteamID.is_valid`

### steam.guard

- Renamed `medium` param to `backend` on `SteamAuthenticator`
- Fixed `create_emergency_codes()` not returning codes
- Fixed `validate_phone_number()` returning no data

### steam.webauth

- Added `WebAuth.cli_login()`, handles all steps of the login process
- Updated `password` param to be optional on `WebAuth`

### steam.client

- Replaced builtin CM server list with automatic discovery via WebAPI or DNS
- UM/ServiceMethods are now handled in the `SteamClient` instance. See `SteamClient.send_um()`
- Messages now have a `payload` property set when the body cannot be parsed
- `get_product_info()` now replaces invalid unicode chars
- `get_product_info()` includes `_missing_token` key with every result
- Added `CDNClient` for downloading connect from SteamPipe
- Added `rich_presence` property to `SteamUser`
- Added block/unblock methods for `SteamUser`
- Added jitter to reconnect delay in `SteamClient`
- Updated protocol version to 65580
- Updated `SteamClient` to use new chat mode, with option to fallback
- Updated `get_product_info()` to include `_missing_token` variable
- Updated protobufs
- Removed `SteamClient.unifed_messages`
- Removed `steam.client.mixins` package
- Removed `Account` builtin as all methods have been deprecated
- Removed `SteamClient.change_email()`
- Removed `SteamClient.create_account()`
