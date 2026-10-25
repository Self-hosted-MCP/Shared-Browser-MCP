#!/usr/bin/env python3
"""Turns your passphrase into the LOGIN_HASH value. Nothing is stored or sent anywhere. Run it on your own computer."""
import getpass, hashlib, secrets, sys

passphrase = getpass.getpass("Passphrase (12+ characters): ")
if len(passphrase) < 12:
    sys.exit("Too short. Use at least 12 characters.")
if passphrase != getpass.getpass("Again: "):
    sys.exit("They do not match.")
rounds, salt = 600_000, secrets.token_bytes(16)
digest = hashlib.pbkdf2_hmac("sha256", passphrase.encode(), salt, rounds)
print(f"\nLOGIN_HASH=pbkdf2:{rounds}:{salt.hex()}:{digest.hex()}\n")
print("Put that in your server's environment settings as LOGIN_HASH (in Coolify, switch 'Is Literal' on). Keep the passphrase in your password manager.")
