from typing import Union


def to_bytes(bytes_or_str: Union[bytes, str]) -> bytes:
    """将字符串转换为bytes"""
    if isinstance(bytes_or_str, str):
        value = bytes_or_str.encode()
    else:
        value = bytes_or_str
    return value
