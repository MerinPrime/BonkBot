import enum


class ForceZoneType(enum.IntEnum):
    ABSOLUTE = 0
    RELATIVE = 1
    CENTER_PUSH = 2
    CENTER_PULL = 3

    @staticmethod
    def from_id(type_id: int) -> 'ForceZoneType':
        for force_zone_type in ForceZoneType:
            if type_id == force_zone_type.value:
                return force_zone_type
