import enum
from typing import Dict, List, Optional, Union


class PSONType(enum.IntEnum):
    MAX = 0xEF
    NULL = 0xF0
    TRUE = 0xF1
    FALSE = 0xF2
    EMPTY_OBJECT = 0xF3
    EMPTY_ARRAY = 0xF4
    EMPTY_STRING = 0xF5
    OBJECT = 0xF6
    ARRAY = 0xF7
    INTEGER = 0xF8
    LONG = 0xF9
    FLOAT = 0xFA
    DOUBLE = 0xFB
    STRING = 0xFC
    STRING_ADD = 0xFD  # UNUSED
    STRING_GET = 0xFE
    BINARY = 0xFF


JsonValue = Optional[Union[str, int, float, bool, List['JsonValue'], Dict[str, 'JsonValue'], bytearray]]
