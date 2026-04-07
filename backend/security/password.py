import base64
import hashlib
import secrets

_HASH_NAME = "sha256"
_ITERATIONS = 200000


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    dk = hashlib.pbkdf2_hmac(_HASH_NAME, password.encode("utf-8"), salt, _ITERATIONS)
    return (
        f"pbkdf2_{_HASH_NAME}${_ITERATIONS}${base64.b64encode(salt).decode()}${base64.b64encode(dk).decode()}"
    )


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        prefix, iterations, salt_b64, digest_b64 = stored_hash.split("$", 3)
        if not prefix.startswith("pbkdf2_"):
            return False
        salt = base64.b64decode(salt_b64)
        expected = base64.b64decode(digest_b64)
        derived = hashlib.pbkdf2_hmac(_HASH_NAME, password.encode("utf-8"), salt, int(iterations))
        return secrets.compare_digest(derived, expected)
    except (ValueError, TypeError):
        return False
