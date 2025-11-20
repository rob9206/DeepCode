from werkzeug.security import generate_password_hash, check_password_hash


def hash_password(password: str) -> str:
    """
    Hash a password using Werkzeug's security module.

    :param password: The password to hash.
    :return: A hashed password.
    """
    return generate_password_hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.

    :param password: The password to verify.
    :param hashed_password: The hashed password to compare against.
    :return: True if the password matches the hash, False otherwise.
    """
    return check_password_hash(hashed_password, password)