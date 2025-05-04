import re

USERNAME_REGEX = re.compile(r"^[A-Za-z0-9_]{2,16}$")

def validate_username(username: str) -> None:
    if not username.isascii():
        raise ValueError("Username must contain only ASCII characters.")

    if not USERNAME_REGEX.fullmatch(username):
        raise ValueError("Username must be 2-16 characters long and contain only letters, numbers, and underscores.")
