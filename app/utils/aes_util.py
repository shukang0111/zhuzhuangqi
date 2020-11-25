import base64
import hashlib
from base64 import b64decode, b64encode
from os import getenv
from typing import Union

from Crypto.Cipher import AES

from .string_util import to_bytes


class AESCrypto:
    """AES加解密"""
    def __init__(self, key_seed: Union[bytes,str]):
        """Initializer
        Args:
            key_seed: 密钥种子，用于生成密钥
        """
        self.mode = AES.MODE_CBC
        self.block_size = AES.block_size
        self.key = hashlib.md5(to_bytes(key_seed)).hexdigest().encode('utf-8')
        # self.key = hashlib.md5(to_bytes(key_seed)).hexdigest()
        self.iv = self.key[:self.block_size]

    def encrypt(self, text: Union[bytes, str]) -> str:
        """AES加密 & BASE64编码"""
        cipher = AES.new(self.key, mode=self.mode, IV=self.iv)
        text = to_bytes(text)
        pad_len = self.block_size - len(text) % self.block_size
        text += bytes([pad_len] * pad_len)
        cipher_data = cipher.encrypt(text)
        return b64encode(cipher_data).decode()

    def decrypt(self, data: Union[bytes, str]) -> str:
        """BASE64解码 & AES解密"""
        cipher = AES.new(self.key, mode=self.mode, IV=self.iv)
        cipher_data = b64decode(data)
        text = cipher.decrypt(cipher_data)
        pad_len = text[-1]
        return text[:-pad_len].decode()


# aes_crypto = AESCrypto(getenv('AES_KEY_SEED'))
aes_crypto = AESCrypto("abc")
