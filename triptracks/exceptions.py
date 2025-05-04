from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

from triptracks.constants import ErrorMessages
from triptracks.enums import ErrorCode

def custom_exception_handler(exc, context):
    # Call DRF's default exception handler first
    response = exception_handler(exc, context)

    if response is not None:
        # Customize the error response here
        # For example, you can modify the response data or status code
        if response.status_code in ErrorMessages:
            error_code = response.status_code
            response.data = {
                'error_message': ErrorMessages[error_code],
                'detail': response.data.get('detail', 'Unknown error')
            }

    return response