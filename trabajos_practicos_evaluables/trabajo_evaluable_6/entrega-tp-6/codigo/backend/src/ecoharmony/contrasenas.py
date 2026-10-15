"""Hash de contrasenas con scrypt (biblioteca estandar: gratis y sin dependencias)."""

import hashlib
import hmac
import os

_N, _R, _P = 2**14, 8, 1


def _derivar(contrasena, sal):
    return hashlib.scrypt(contrasena.encode("utf-8"), salt=sal, n=_N, r=_R, p=_P)


def hashear(contrasena):
    """Devuelve 'scrypt$<sal>$<hash>'; cada llamada usa una sal aleatoria distinta."""
    sal = os.urandom(16)
    return f"scrypt${sal.hex()}${_derivar(contrasena, sal).hex()}"


def verificar(contrasena, almacenado):
    try:
        algoritmo, sal_hex, hash_hex = almacenado.split("$")
        sal = bytes.fromhex(sal_hex)
    except (ValueError, AttributeError):
        return False
    if algoritmo != "scrypt":
        return False
    return hmac.compare_digest(_derivar(contrasena, sal).hex(), hash_hex)
