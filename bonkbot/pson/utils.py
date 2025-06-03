def zigzag_encode32(value: int) -> int:
    return (value << 1) ^ (value >> 31) & 0xFFFFFFFF

def zigzag_decode32(value: int) -> int:
    return (value >> 1) ^ -(value & 1) & 0xFFFFFFFF

def zigzag_encode64(value: int) -> int:
    return (value << 1) ^ (value >> 63) & 0xFFFFFFFFFFFFFFFF

def zigzag_decode64(value: int) -> int:
    return (value >> 1) ^ -(value & 1) & 0xFFFFFFFFFFFFFFFF
