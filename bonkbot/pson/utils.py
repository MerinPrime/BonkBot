import struct


def is_double(value: float) -> bool:
    try:
        packed_f32 = struct.pack('>f', value)
        unpacked_f32 = struct.unpack('>f', packed_f32)[0]
        return value != unpacked_f32
    except OverflowError:
        return True


def zigzag_encode32(n: int) -> int:
    return (n << 1) ^ (n >> 31)


def zigzag_decode32(n: int) -> int:
    return (n >> 1) ^ -(n & 1)


def zigzag_encode64(n: int) -> int:
    return (n << 1) ^ (n >> 63)


def zigzag_decode64(n: int) -> int:
    return (n >> 1) ^ -(n & 1)
