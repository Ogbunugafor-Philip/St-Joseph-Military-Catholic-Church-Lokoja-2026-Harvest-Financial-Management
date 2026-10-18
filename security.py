"""Authentication and configuration helpers for the Harvest application."""

from __future__ import annotations

import hashlib
import hmac
import os
import secrets
from pathlib import Path

from dotenv import load_dotenv

PROJECT_DIR = Path(__file__).resolve().parent
load_dotenv(PROJECT_DIR / ".env", override=False)

PBKDF2_ITERATIONS = 600_000


class ConfigurationError(RuntimeError):
    """Raised when required secure configuration is absent or invalid."""


def hash_password(password: str, *, iterations: int = PBKDF2_ITERATIONS) -> str:
    if not password:
        raise ValueError("Password must not be empty.")
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return f"pbkdf2_sha256${iterations}${salt.hex()}${digest.hex()}"


def verify_password(password: str, encoded: str) -> bool:
    try:
        algorithm, raw_iterations, salt_hex, expected_hex = encoded.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        iterations = int(raw_iterations)
        if iterations < 100_000:
            return False
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(expected_hex)
    except (AttributeError, TypeError, ValueError):
        return False
    actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return hmac.compare_digest(actual, expected)


def required_password_hash(variable_name: str) -> str:
    value = os.environ.get(variable_name, "").strip()
    if not value:
        raise ConfigurationError(f"Required secure configuration {variable_name} is not set.")
    if not value.startswith("pbkdf2_sha256$"):
        raise ConfigurationError(f"{variable_name} must contain a PBKDF2 password hash.")
    return value

def integer_setting(variable_name: str, default: int, *, minimum: int, maximum: int) -> int:
    raw = os.environ.get(variable_name, str(default))
    try:
        value = int(raw)
    except ValueError as exc:
        raise ConfigurationError(f"{variable_name} must be an integer.") from exc
    if not minimum <= value <= maximum:
        raise ConfigurationError(f"{variable_name} must be between {minimum} and {maximum}.")
    return value
