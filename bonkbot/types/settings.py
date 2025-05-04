from dataclasses import dataclass

from bonkbot.pson import ByteBuffer


# Source: https://github.com/MerinPrime/ReBonk/blob/master/src/core/CustomControls.ts
@dataclass
class Settings:
    version: int = 6
    up1: int = 38
    down1: int = 40
    left1: int = 37
    right1: int = 39
    heavy1: int = 88
    special1: int = 90
    up2: int = 87
    down2: int = 83
    left2: int = 65
    right2: int = 68
    heavy2: int = 16
    special2: int = 89
    up3: int = 999
    down3: int = 999
    left3: int = 999
    right3: int = 999
    heavy3: int = 32
    special3: int = 999
    filter: bool = True
    stats: bool = False
    help: bool = True
    quality: int = 3

    @staticmethod
    def from_buffer(buffer: ByteBuffer) -> "Settings":
        settings = Settings()
        settings.version = buffer.read_uint16()

        if settings.version >= 1:
            settings.up1 = buffer.read_uint16()
            settings.up2 = buffer.read_uint16()
            settings.down1 = buffer.read_uint16()
            settings.down2 = buffer.read_uint16()
            settings.left1 = buffer.read_uint16()
            settings.left2 = buffer.read_uint16()
            settings.right1 = buffer.read_uint16()
            settings.right2 = buffer.read_uint16()
            settings.heavy1 = buffer.read_uint16()
            settings.heavy2 = buffer.read_uint16()
            settings.special1 = buffer.read_uint16()
            settings.special2 = buffer.read_uint16()

        if settings.version >= 2:
            settings.filter = buffer.read_uint8() == 1

        if settings.version >= 3:
            settings.stats = buffer.read_uint8() == 1

        if 3 <= settings.version <= 5:
            legacyQualityFlag = buffer.read_uint8() == 1
            if legacyQualityFlag:
                settings.quality = 3
            else:
                settings.quality = 2

        if settings.version >= 4:
            settings.help = buffer.read_uint8() == 1

        if settings.version >= 3:
            settings.up3 = buffer.read_uint16()
            settings.down3 = buffer.read_uint16()
            settings.left3 = buffer.read_uint16()
            settings.right3 = buffer.read_uint16()
            settings.heavy3 = buffer.read_uint16()
            settings.special3 = buffer.read_uint16()

        if settings.version >= 6:
            settings.quality = buffer.read_uint16()

        return settings
