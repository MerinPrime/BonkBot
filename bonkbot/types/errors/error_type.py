import enum


class ErrorType(enum.Enum):
    RATE_LIMITED = 'ratelimited'
    PASSWORD = 'password'
    USERNAME_FAIL = 'username_fail'
    NOT_HOST = 'not_host'
    INVALID_BALANCE = 'invalid_balance'
    ROOM_NOT_FOUND = 'roomnotfound'
    HOST_CHANGE_RATE_LIMITED = 'host change rate limited'
    NEW_HOST_NOT_PRESENT = 'new_host_not_present'

    @staticmethod
    def from_string(code: str) -> 'ErrorType':
        for error_type in ErrorType:
            if error_type.value == code:
                return error_type
        raise ValueError(f'{code} is not a valid error code')
