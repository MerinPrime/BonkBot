from typing import Union


class T:
    ZERO = 0x00
    MAX = 0xEF
    NULL = 0xF0
    TRUE = 0xF1
    FALSE = 0xF2
    EOBJECT = 0xF3
    EARRAY = 0xF4
    ESTRING = 0xF5
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


PsonValue = Union[str, int, float, bool, list, dict, bytearray]
