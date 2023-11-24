"""misc security-related utils"""
import bcrypt


def bcrypt_hash(cleartext: str) -> str:
    """
    hash the given cleartext password using bcrypt and return a string value
    suitable for storage in a database
    """
    return bcrypt.hashpw(
        cleartext.encode("utf-8", errors="strict"),
        bcrypt.gensalt(prefix=b"2a"),
    ).decode("utf-8", errors="strict")
