from enum import IntEnum


class SteamIntEnum(IntEnum):
    def __str__(self):
        return self.name
