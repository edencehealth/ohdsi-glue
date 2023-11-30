"""misc security-related utils"""
import bcrypt


def bcrypt_hash(cleartext_password: str) -> str:
    """
    hash the given cleartext password using bcrypt and return a string value
    suitable for storage in a database
    """
    return bcrypt.hashpw(
        cleartext_password.encode("utf-8", errors="strict"),
        bcrypt.gensalt(prefix=b"2a"),
    ).decode("utf-8", errors="strict")


def bcrypt_check(password: str, hashed_password: str) -> bool:
    """
    return true if the given cleartext password matches the given hashed password
    """
    return bcrypt.checkpw(
        password.encode("utf-8", errors="strict"),
        hashed_password.encode("utf-8", errors="strict"),
    )
