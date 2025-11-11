"""
Script to generate a secure random secret key
"""
import sys
import secrets


def generate_secret_key():
    """Generate a secure random secret key"""
    secret_key = secrets.token_urlsafe(32)
    print(f"Generated SECRET_KEY: {secret_key}")
    print("\nCopy this key to your .env file:")
    print(f"SECRET_KEY={secret_key}")
    return secret_key


if __name__ == "__main__":
    generate_secret_key()

