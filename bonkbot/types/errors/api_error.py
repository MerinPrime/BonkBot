from bonkbot.types.errors import ErrorType


class ApiError(Exception):
    error_type: ErrorType

    def __init__(self, error_code: str):
        self.error_type = ErrorType.from_string(error_code)
        super().__init__(self.error_type)
