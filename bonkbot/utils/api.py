import re
from typing import Optional

from ..types.errors.error_type import ErrorType

USERNAME_REGEX = re.compile(r'^[A-Za-z0-9_ ]{2,16}$')

def validate_username(username: str, *, is_guest: bool) -> Optional[ErrorType]:
    """
    Validates the provided username and returns the corresponding error type if it is invalid.
        
    :param username: The username to validate.
    :param is_guest: Whether the username is for a guest (as opposed to an account).
    :return: An ErrorType if the username is invalid; otherwise, None.
    """

    if not username.isascii():
        return ErrorType.USERNAME_MUST_BE_ASCII

    if len(username) < 2:
        return ErrorType.USERNAME_TOO_SHORT

    if len(username) > 15:
        return ErrorType.USERNAME_TOO_LONG

    if not USERNAME_REGEX.fullmatch(username):
        return ErrorType.USERNAME_INVALID_CHARS

    if username.startswith(' '):
        return ErrorType.USERNAME_INVALID_START

    if not is_guest:
        if username.startswith('_'):
            return ErrorType.USERNAME_INVALID_START

        if '  ' in username:
            return ErrorType.USERNAME_INVALID_CHARS

    return None
