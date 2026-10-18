#!/usr/bin/env python3
"""Generate a PBKDF2 password hash without echoing the password."""

from getpass import getpass
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from security import hash_password  # noqa: E402


def main() -> None:
    first = getpass("Password: ")
    second = getpass("Confirm password: ")
    if first != second:
        raise SystemExit("Passwords do not match.")
    print(hash_password(first))


if __name__ == "__main__":
    main()
