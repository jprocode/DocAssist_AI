#!/usr/bin/env python3
"""
Utility script to generate bcrypt password hash for authentication.
Usage: python generate_password_hash.py <password>
"""
import sys
from utils.security import hash_password

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate_password_hash.py <password>")
        sys.exit(1)
    
    password = sys.argv[1]
    hashed = hash_password(password)
    print(f"\nPassword hash generated:")
    print(f"AUTH_PASSWORD_HASH={hashed}")
    print(f"\nAdd this to your .env file (backend and frontend).")
    print(f"Remove AUTH_PASSWORD if you're using the hash.")

