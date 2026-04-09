import base64
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

from app.core.config import settings


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def get_jwks() -> dict:
    path = Path(settings.jwt_public_key_path)
    pem_content = path.read_bytes()
    pub = serialization.load_pem_public_key(pem_content, backend=default_backend())
    numbers = pub.public_numbers()
    n_bytes = numbers.n.to_bytes((numbers.n.bit_length() + 7) // 8, "big")
    e_bytes = numbers.e.to_bytes((numbers.e.bit_length() + 7) // 8, "big")
    return {
        "keys": [
            {
                "kty": "RSA",
                "kid": "user-service-key-1",
                "use": "sig",
                "alg": "RS256",
                "n": _b64url(n_bytes),
                "e": _b64url(e_bytes),
            }
        ]
    }
