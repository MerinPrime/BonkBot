import enum


class CaptureType(enum.IntEnum):
    NORMAL = 0
    INSTANT_RED = 1
    INSTANT_BLUE = 2
    INSTANT_GREEN = 3
    INSTANT_YELLOW = 4

    @staticmethod
    def from_id(type_id: int) -> 'CaptureType':
        for capture_type in CaptureType:
            if type_id == capture_type.value:
                return capture_type
