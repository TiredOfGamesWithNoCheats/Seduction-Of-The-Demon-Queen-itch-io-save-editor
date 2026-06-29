from pathlib import Path
from hashlib import md5
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import struct

KEY = b"my_secret_key_123456789012345678"

MAGIC = 0x43454447       # "GDEC"
MODE_AES256 = 1
BLOCK_SIZE = 16


class GodotCryptoError(Exception):
    pass


class GodotCrypto:

    @staticmethod
    def _pad(data: bytes) -> bytes:
        pad = (-len(data)) % BLOCK_SIZE
        return data + b"\x00" * pad

    @staticmethod
    def encrypt(plaintext: bytes) -> bytes:

        padded = GodotCrypto._pad(plaintext)

        iv = get_random_bytes(16)

        cipher = AES.new(
            KEY,
            AES.MODE_CFB,
            iv=iv,
            segment_size=128
        )

        encrypted = cipher.encrypt(padded)

        out = bytearray()

        out += struct.pack("<I", MAGIC)
        out += md5(plaintext).digest()
        out += struct.pack("<Q", len(plaintext))
        out += iv
        out += encrypted

        return bytes(out)

    @staticmethod
    def decrypt(data: bytes) -> bytes:

        if len(data) < 44:
            raise GodotCryptoError("File too small.")

        magic = struct.unpack("<I", data[:4])[0]

        if magic != MAGIC:
            raise GodotCryptoError("Invalid GDEC header.")

        expected_md5 = data[4:20]

        original_size = struct.unpack("<Q", data[20:28])[0]

        iv = data[28:44]

        encrypted = data[44:]

        cipher = AES.new(
            KEY,
            AES.MODE_CFB,
            iv=iv,
            segment_size=128
        )

        plaintext = cipher.decrypt(encrypted)

        plaintext = plaintext[:original_size]

        if md5(plaintext).digest() != expected_md5:
            raise GodotCryptoError(
                "Invalid key or corrupted save."
            )

        return plaintext

    @staticmethod
    def load(path: str) -> bytes:
        return GodotCrypto.decrypt(Path(path).read_bytes())

    @staticmethod
    def save(path: str, plaintext: bytes):
        Path(path).write_bytes(
            GodotCrypto.encrypt(plaintext)
        )