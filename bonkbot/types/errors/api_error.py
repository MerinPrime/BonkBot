from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .error_type import ErrorType


class ApiError(Exception):
    error_type: 'ErrorType'

    def __init__(self, error_type: 'ErrorType'):
        self.error_type = error_type
        super().__init__(self.error_type)
