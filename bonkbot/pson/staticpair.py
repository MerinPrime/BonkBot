from typing import List, Optional, Union

from .bytebuffer import ByteBuffer
from .type import JsonValue, PSONType
from .utils import (
    is_double,
    zigzag_decode32,
    zigzag_decode64,
    zigzag_encode32,
    zigzag_encode64,
)


class StaticPair:
    hash_dict: dict
    ihash_dict: dict
    next_idx: int

    def __init__(self, keys: Optional[List[str]]) -> None:
        self.hash_dict = {}
        self.next_idx = 0

        if keys is not None:
            for i, v in enumerate(keys):
                self.hash_dict[v] = i
            self.next_idx = len(keys)
            self.ihash_dict = {v: k for k, v in self.hash_dict.items()}

    def encode(self, value: Optional[JsonValue], buffer: 'ByteBuffer' = None) -> 'ByteBuffer':
        if buffer is None:
            buffer = ByteBuffer()

        endian = buffer.endian
        buffer.set_little_endian()
        self.encode_value(value, buffer)
        buffer.set_endian(endian)
        return buffer

    def encode_value(self, value: Optional[JsonValue], buffer: 'ByteBuffer' = None) -> 'ByteBuffer':
        if value is None:
            buffer.write_uint8(PSONType.NULL)
        elif type(value) is str:
            if value == '':
                buffer.write_uint8(PSONType.ESTRING)
            elif value in self.hash_dict:
                buffer.write_uint8(PSONType.STRING_GET)
                buffer.write_uint8(self.hash_dict[value])
            else:
                buffer.write_uint8(PSONType.STRING)
                buffer.write_str(value)
        elif type(value) is int:
            if value <= 0xFFFFFFFF:
                zzval = zigzag_encode32(value)
                if zzval < PSONType.MAX:
                    buffer.write_uint8(zzval)
                else:
                    buffer.write_uint8(PSONType.INTEGER)
                    buffer.write_varint32(zzval)
            else:
                buffer.write_uint8(PSONType.LONG)
                zzval = zigzag_encode64(value)
                buffer.write_varint64(zzval)
        elif type(value) is float:
            if is_double(value):
                buffer.offset -= 4
                buffer.write_uint8(PSONType.FLOAT)
                buffer.write_float32(value)
            else:
                buffer.offset -= 4
                buffer.write_uint8(PSONType.DOUBLE)
                buffer.write_float64(value)
        elif type(value) is bool:
            buffer.write_uint8(PSONType.TRUE if value else PSONType.FALSE)
        elif type(value) is list:
            if len(value) == 0:
                buffer.write_uint8(PSONType.EARRAY)
            else:
                buffer.write_uint8(PSONType.ARRAY)
                buffer.write_varint64(len(value))
                for i in value:
                    self.encode(i, buffer)
        elif type(value) is dict:
            filtered_value = {k: v for k, v in value.items() if v is not None}
            if len(filtered_value) == 0:
                buffer.write_uint8(PSONType.EOBJECT)
            else:
                buffer.write_uint8(PSONType.OBJECT)
                buffer.write_varint32(len(filtered_value))
                for k, v in filtered_value.items():
                    if k in self.hash_dict:
                        buffer.write_uint8(PSONType.STRING_GET)
                        buffer.write_varint32(self.hash_dict[k])
                    else:
                        buffer.write_uint8(PSONType.STRING)
                        buffer.write_str(k)
                    self.encode(v, buffer)
        else:
            raise TypeError(type(value).__name__)

        return buffer

    def decode(self, _bytes: Union[bytearray, 'ByteBuffer']) -> JsonValue:
        if type(_bytes) is bytearray:
            buffer = ByteBuffer(_bytes)
        else:
            buffer = _bytes

        endian = buffer.endian
        buffer.set_little_endian()
        data = self.decode_value(buffer)
        buffer.set_endian(endian)
        return data

    def decode_value(self, buffer: 'ByteBuffer') -> JsonValue:
        code = buffer.read_uint8()
        if code <= PSONType.MAX:
            return zigzag_decode32(code)

        if code == PSONType.NULL:
            return None
        if code == PSONType.TRUE:
            return True
        if code == PSONType.FALSE:
            return False
        if code == PSONType.EOBJECT:
            return {}
        if code == PSONType.EARRAY:
            return []
        if code == PSONType.ESTRING:
            return ''
        if code == PSONType.OBJECT:
            obj = {}
            for _ in range(buffer.read_varint32()):
                key = self.decode(buffer)
                value = self.decode(buffer)
                try:
                    obj[key] = value
                except TypeError:
                    pass
            return obj
        if code == PSONType.ARRAY:
            arr = []
            for _ in range(buffer.read_varint32()):
                arr.append(self.decode(buffer))
            return arr
        if code == PSONType.INTEGER:
            return zigzag_decode32(buffer.read_varint32())
        if code == PSONType.LONG:
            return zigzag_decode64(buffer.read_varint64())
        if code == PSONType.FLOAT:
            return buffer.read_float32()
        if code == PSONType.DOUBLE:
            return buffer.read_float64()
        if code == PSONType.STRING:
            return buffer.read_str()
        if code == PSONType.STRING_GET:
            return self.ihash_dict[buffer.read_uint8()]
        if code == PSONType.BINARY:
            return buffer.read_bytes(buffer.read_varint32())
