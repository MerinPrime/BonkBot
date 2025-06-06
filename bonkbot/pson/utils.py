def zigzag_encode32(n: int) -> int:
    return (n << 1) ^ (n >> 31)

def zigzag_decode32(n: int) -> int:
    return (n >> 1) ^ -(n & 1)

def zigzag_encode64(n: int) -> int:
    return (n << 1) ^ (n >> 63)

def zigzag_decode64(n: int) -> int:
    return (n >> 1) ^ -(n & 1)
