import base64
import struct
from typing import Optional
from urllib.parse import unquote

from lzstring import LZString


class ByteBuffer:
    __slots__ = ('bytes', 'endian', 'offset')

    def __init__(self, _bytes: Optional[bytearray] = None) -> None:
        if _bytes is None:
            self.bytes: bytearray = bytearray()
        else:
            self.bytes: bytearray = _bytes
        self.offset: int = 0
        self.endian: str = '>'
    
    @property
    def size(self) -> int:
        return len(self.bytes)
    
    def set_endian(self, endian: str) -> None:
        self.endian = endian

    def set_little_endian(self) -> None:
        self.endian = '<'

    def set_big_endian(self) -> None:
        self.endian = '>'

    def read_bytes(self, count: int = 1) -> bytearray:
        self.offset += count
        return self.bytes[self.offset-count:self.offset]

    def from_base64(self, data: str, *, uri_encoded: bool = False,
                    lz_encoded: bool = False, case_encoded: bool = False) -> 'ByteBuffer':
        if uri_encoded:
            data = unquote(data)
        if case_encoded:
            temp_data = ''
            for i, char in enumerate(data):
                if i <= 100 and char.islower():
                    temp_data += char.upper()
                elif i <= 100 and char.isupper():
                    temp_data += char.lower()
                else:
                    temp_data += char
            data = temp_data
        if lz_encoded:
            data = LZString.decompressFromEncodedURIComponent(data)
        self.bytes += base64.b64decode(data)
        return self

    def read_uint8(self) -> int:
        return struct.unpack(self.endian + 'B', self.read_bytes(1))[0]

    def read_int8(self) -> int:
        return struct.unpack(self.endian + 'b', self.read_bytes(1))[0]

    def read_uint16(self) -> int:
        return struct.unpack(self.endian + 'H', self.read_bytes(2))[0]

    def read_int16(self) -> int:
        return struct.unpack(self.endian + 'h', self.read_bytes(2))[0]

    def read_uint32(self) -> int:
        return struct.unpack(self.endian + 'I', self.read_bytes(4))[0]

    def read_int32(self) -> int:
        return struct.unpack(self.endian + 'i', self.read_bytes(4))[0]

    def read_uint64(self) -> int:
        return struct.unpack(self.endian + 'Q', self.read_bytes(8))[0]

    def read_int64(self) -> int:
        return struct.unpack(self.endian + 'q', self.read_bytes(8))[0]

    def read_varint32(self) -> int:
        value = 0
        shift = 0
        for _ in range(4):
            byte = self.read_uint8()
            value |= (byte & 0x7F) << shift
            shift += 7
            if (byte & 0x80) == 0:
                break
        return value

    def read_varint64(self) -> int:
        value = 0
        shift = 0
        for _ in range(8):
            byte = self.read_uint8()
            value |= (byte & 0x7F) << shift
            shift += 7
            if (byte & 0x80) == 0:
                break
        return value

    def read_float32(self) -> float:
        return struct.unpack(self.endian + 'f', self.read_bytes(4))[0]

    def read_float64(self) -> float:
        return struct.unpack(self.endian + 'd', self.read_bytes(8))[0]

    def read_str(self) -> str:
        length = self.read_uint8()
        return self.read_bytes(length).decode('utf-8')

    def read_utf(self) -> str:
        length = self.read_uint16()
        return self.read_bytes(length).decode('utf-8')

    def read_vstr(self) -> float:
        length = self.read_varint32()
        return self.read_bytes(length).decode('utf-8')

    def write_bytes(self, _bytes: bytearray) -> None:
        empty = self.size - self.offset
        if empty < len(_bytes):
            needed = len(_bytes) - empty
            self.bytes.extend(b'\x00' * needed)
        self.bytes[self.offset:self.offset+len(_bytes)] = _bytes
        self.offset += len(_bytes)

    def write_uint8(self, value: int) -> None:
        self.write_bytes(struct.pack(self.endian + 'B', value))

    def write_bool(self, value: bool) -> None:
        self.write_uint8(int(value))

    def write_int8(self, value: int) -> None:
        self.write_bytes(struct.pack(self.endian + 'b', value))

    def write_uint16(self, value: int) -> None:
        self.write_bytes(struct.pack(self.endian + 'H', value))

    def write_int16(self, value: int) -> None:
        self.write_bytes(struct.pack(self.endian + 'h', value))

    def write_uint32(self, value: int) -> None:
        self.write_bytes(struct.pack(self.endian + 'I', value))

    def write_int32(self, value: int) -> None:
        self.write_bytes(struct.pack(self.endian + 'i', value))

    def write_uint64(self, value: int) -> None:
        self.write_bytes(struct.pack(self.endian + 'Q', value))

    def write_int64(self, value: int) -> None:
        self.write_bytes(struct.pack(self.endian + 'q', value))

    def write_varint32(self, value: int) -> None:
        _bytes = []
        for _ in range(4):
            byte = value & 0x7F
            value >>= 7
            if value == 0:
                _bytes.append(byte)
                break
            _bytes.append(byte | 0x80)
        self.write_bytes(_bytes)

    def write_varint64(self, value: int) -> None:
        _bytes = []
        for _ in range(8):
            byte = value & 0x7F
            value >>= 7
            if value == 0:
                _bytes.append(byte)
                break
            _bytes.append(byte | 0x80)
        self.write_bytes(_bytes)

    def write_float32(self, value: float) -> None:
        self.write_bytes(struct.pack(self.endian + 'f', value))

    def write_float64(self, value: float) -> None:
        self.write_bytes(struct.pack(self.endian + 'd', value))

    def write_str(self, value: str) -> None:
        bs = value.encode('utf-8')
        self.write_uint8(len(bs))
        self.write_bytes(bs)

    def write_utf(self, value: str) -> None:
        bs = value.encode('utf-8')
        self.write_uint16(len(bs))
        self.write_bytes(bs)

    def write_vstr(self, value: str) -> None:
        bs = value.encode('utf-8')
        self.write_varint32(len(bs))
        self.write_bytes(bs)

    def read_bool(self) -> bool:
        return self.read_uint8() == 1
