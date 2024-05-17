
from enum import Enum


class ErrorCode(Enum):
    BAD_REQUEST = 400
    ACCESS_DENIED = 401
    PAYMENT_REQUIRED = 402
    FORBIDDEN = 403
    RESOURCE_NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    IM_A_TEAPOT = 418
    UPGRADE_REQUIRED = 426
    TOO_MANY_REQUESTS = 429
    UNAVAILABLE_FOR_LEGAL = 451
    INTERNAL_SERVER_ERROR = 500
    NOT_IMPLEMENTED = 501
    SERVICE_UNAVAILABLE = 503


    @classmethod
    def get_code(cls, error_code):
        return cls(error_code)
