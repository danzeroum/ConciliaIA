#!/usr/bin/env python3
"""Generate password hash for test user."""

from argon2 import PasswordHasher


def main() -> None:
    ph = PasswordHasher()
    password = "SecurePassword123!"
    hash_result = ph.hash(password)

    print("Password hash:")
    print(hash_result)
    print("\nUse this hash in auth.py")


if __name__ == "__main__":
    main()
