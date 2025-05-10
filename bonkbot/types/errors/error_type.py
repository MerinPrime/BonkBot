import enum


class ErrorType(enum.Enum):
    RATE_LIMITED = 'ratelimited'
    PASSWORD = 'password'
    USERNAME_FAIL = 'username_fail'
    NOT_HOST = 'not_host'
    INVALID_BALANCE = 'invalid_balance'

    @staticmethod
    def from_string(code: str) -> 'ErrorType':
        for error_type in ErrorType:
            if error_type.value == code:
                return error_type
        raise ValueError(f'{code} is not a valid error code')
