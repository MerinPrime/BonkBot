import base64
import struct
from typing import Optional
from urllib.parse import unquote


def zigzag_encode32(value: int) -> int:
    return (((value | 1) << 1) ^ (value >> 31)) & 0xFFFFFFFF


def zigzag_decode32(value: int) -> int:
    return ((value >> 1) ^ -(value & 1)) & 0xFFFFFFFF


def zigzag_encode64(value: int) -> int:
    return (((value | 1) << 1) ^ (value >> 63)) & 0xFFFFFFFFFFFFFFFF


def zigzag_decode64(value: int) -> int:
    return ((value >> 1) ^ -(value & 1)) & 0xFFFFFFFFFFFFFFFF


class ByteBuffer:
    bytes: bytearray
    offset: int
    size: int

    def __init__(self, bytes: Optional[bytearray] = None) -> None:
        if bytes is None:
            self.bytes = bytearray()
        else:
            self.bytes = bytes
        self.offset = 0
        self.size = len(self.bytes)

    def from_base64(self, data: str, *, uri_encoded: bool = False) -> 'ByteBuffer':
        if uri_encoded:
            data = unquote(data)
        self.bytes += base64.b64decode(data)
        return self

    def read_bytes(self, count: int = 1) -> bytearray:
        self.offset += count
        return self.bytes[self.offset-count:self.offset]

    def read_uint8(self) -> int:
        return struct.unpack('>B', self.read_bytes(1))[0]

    def read_int8(self) -> int:
        return struct.unpack('>b', self.read_bytes(1))[0]

    def read_uint16(self) -> int:
        return struct.unpack('>H', self.read_bytes(2))[0]

    def read_int16(self) -> int:
        return struct.unpack('>h', self.read_bytes(2))[0]

    def read_uint32(self) -> int:
        return struct.unpack('>I', self.read_bytes(4))[0]

    def read_int32(self) -> int:
        return struct.unpack('>i', self.read_bytes(4))[0]

    def read_uint64(self) -> int:
        return struct.unpack('>Q', self.read_bytes(8))[0]

    def read_int64(self) -> int:
        return struct.unpack('>q', self.read_bytes(8))[0]

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
        return struct.unpack('>f', self.read_bytes(4))[0]

    def read_float64(self) -> float:
        return struct.unpack('>d', self.read_bytes(8))[0]

    def read_str(self) -> float:
        length = self.read_uint8()
        return self.read_bytes(length).decode('utf-8')

    def read_vstr(self) -> float:
        length = self.read_varint32()
        return self.read_bytes(length).decode('utf-8')

    def write_bytes(self, _bytes: bytearray) -> None:
        empty = self.size - self.offset
        if empty < len(_bytes):
            needed = len(_bytes) - empty
            alloc = self.size + needed
            alloc = alloc // 16
            alloc = (alloc + 1) * 16
            self.bytes.extend(b'\x00' * (alloc - needed))
            self.size = len(self.bytes)
        self.bytes[self.offset:self.offset+len(_bytes)] = _bytes
        self.offset += len(_bytes)

    def write_uint8(self, value: int) -> None:
        self.write_bytes(struct.pack('>B', value))

    def write_int8(self, value: int) -> None:
        self.write_bytes(struct.pack('>b', value))

    def write_uint16(self, value: int) -> None:
        self.write_bytes(struct.pack('>H', value))

    def write_int16(self, value: int) -> None:
        self.write_bytes(struct.pack('>h', value))

    def write_uint32(self, value: int) -> None:
        self.write_bytes(struct.pack('>I', value))

    def write_int32(self, value: int) -> None:
        self.write_bytes(struct.pack('>i', value))

    def write_uint64(self, value: int) -> None:
        self.write_bytes(struct.pack('>Q', value))

    def write_int64(self, value: int) -> None:
        self.write_bytes(struct.pack('>q', value))

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
        self.write_bytes(struct.pack('>f', value))

    def write_float64(self, value: float) -> None:
        self.write_bytes(struct.pack('>d', value))

    def write_str(self, value: str) -> None:
        bs = value.encode('utf-8')
        self.write_uint8(len(bs))
        self.write_bytes(bs)

    def write_vstr(self, value: str) -> None:
        bs = value.encode('utf-8')
        self.write_varint32(len(bs))
        self.write_bytes(bs)

    def flipped(self) -> None:
        return self.bytes[::-1]
