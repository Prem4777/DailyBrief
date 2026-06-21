"""
services/credential_service.py — Fernet symmetric encryption for OAuth tokens.

All OAuth / API tokens stored in UserCredential.token_data are encrypted at
rest using a Fernet key loaded from settings.credential_encryption_key.

The key must be a URL-safe base64-encoded 32-byte value.
Generate one with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
"""

from __future__ import annotations

import json

from cryptography.fernet import Fernet, InvalidToken

from config import settings


def _get_fernet() -> Fernet:
    """Construct a Fernet instance from the configured encryption key.

    Raises:
        ValueError: if credential_encryption_key is not set or is invalid.
    """
    key = settings.credential_encryption_key
    if not key:
        raise ValueError(
            "CREDENTIAL_ENCRYPTION_KEY is not set. "
            "Generate one and add it to your .env file."
        )
    # TODO: cache the Fernet instance if construction overhead becomes measurable
    return Fernet(key.encode() if isinstance(key, str) else key)


def encrypt_token_data(data: dict) -> str:
    """Serialize `data` to JSON and encrypt it with Fernet.

    Args:
        data: A dict of token fields (e.g. {"access_token": "...", "refresh_token": "..."}).

    Returns:
        A URL-safe base64-encoded ciphertext string suitable for DB storage.
    """
    fernet = _get_fernet()
    plaintext = json.dumps(data).encode("utf-8")
    ciphertext_bytes = fernet.encrypt(plaintext)
    return ciphertext_bytes.decode("utf-8")


def decrypt_token_data(encrypted: str) -> dict:
    """Decrypt and deserialize a Fernet-encrypted token blob.

    Args:
        encrypted: The ciphertext string retrieved from UserCredential.token_data.

    Returns:
        The original token dict.

    Raises:
        InvalidToken: if the ciphertext is tampered with or the key is wrong.
        json.JSONDecodeError: if the decrypted bytes are not valid JSON.
    """
    fernet = _get_fernet()
    # TODO: handle token rotation (Fernet.MultiFernet) if key rotation is needed
    plaintext_bytes = fernet.decrypt(encrypted.encode("utf-8"))
    return json.loads(plaintext_bytes.decode("utf-8"))
