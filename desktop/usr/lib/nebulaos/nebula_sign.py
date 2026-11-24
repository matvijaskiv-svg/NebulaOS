"""Ed25519 signatures for the NebulaOS channel (libsodium via ctypes).

The maintainer signs channel.json with a private key that exists only on their
computer; every NebulaOS checks it with /usr/share/nebulaos/admin.pub.
News, polls, the ban list, official groups and update holds are trusted only if
the signature is valid.
"""
import ctypes as C
from pathlib import Path

PUBLIC_KEY = Path("/usr/share/nebulaos/admin.pub")
_lib = C.CDLL("libsodium.so.26") if Path("/usr/lib/libsodium.so.26").exists() else C.CDLL("libsodium.so")
_lib.sodium_init()


def keypair():
    """New (public_hex, secret_hex)."""
    pk, sk = C.create_string_buffer(32), C.create_string_buffer(64)
    _lib.crypto_sign_keypair(pk, sk)
    return pk.raw.hex(), sk.raw.hex()


def sign(secret_hex, data: bytes):
    sig = C.create_string_buffer(64)
    _lib.crypto_sign_detached(sig, None, data, C.c_ulonglong(len(data)), bytes.fromhex(secret_hex))
    return sig.raw.hex()


def verify(public_hex, data: bytes, sig_hex):
    try:
        sig, pk = bytes.fromhex(sig_hex.strip()), bytes.fromhex(public_hex.strip())
    except ValueError:
        return False
    if len(sig) != 64 or len(pk) != 32:
        return False
    return _lib.crypto_sign_verify_detached(sig, data, C.c_ulonglong(len(data)), pk) == 0


def trusted(data: bytes, sig_hex):
    """Is this channel content signed by the NebulaOS maintainer?"""
    try:
        pub = PUBLIC_KEY.read_text().strip()
    except OSError:
        return False
    return verify(pub, data, sig_hex or "")
