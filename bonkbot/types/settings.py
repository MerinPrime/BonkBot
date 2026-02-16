from typing import TYPE_CHECKING

from attrs import define, field

if TYPE_CHECKING:
    from ..pson.bytebuffer import ByteBuffer


# Source: https://github.com/MerinPrime/ReBonk/blob/master/src/core/CustomControls.ts
@define(slots=True, auto_attribs=True)
class Settings:
    version: int = field(default=6)

    up1: int = field(default=38)
    down1: int = field(default=40)
    left1: int = field(default=37)
    right1: int = field(default=39)
    heavy1: int = field(default=88)
    special1: int = field(default=90)

    up2: int = field(default=87)
    down2: int = field(default=83)
    left2: int = field(default=65)
    right2: int = field(default=68)
    heavy2: int = field(default=16)
    special2: int = field(default=89)

    up3: int = field(default=999)
    down3: int = field(default=999)
    left3: int = field(default=999)
    right3: int = field(default=999)
    heavy3: int = field(default=32)
    special3: int = field(default=999)

    filter: bool = field(default=True)
    stats: bool = field(default=False)
    help: bool = field(default=True)

    quality: int = field(default=3)

    @staticmethod
    def from_buffer(buffer: 'ByteBuffer') -> 'Settings':
        settings = Settings()
        if buffer.size == 0:
            return settings
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
            settings.filter = buffer.read_bool()

        if settings.version >= 3:
            settings.stats = buffer.read_bool()

        if 3 <= settings.version <= 5:
            legacyQualityFlag = buffer.read_bool()
            if legacyQualityFlag:
                settings.quality = 3
            else:
                settings.quality = 2

        if settings.version >= 4:
            settings.help = buffer.read_bool()

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
