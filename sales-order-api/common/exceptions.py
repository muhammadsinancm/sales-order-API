from rest_framework.views import exception_handler
from rest_framework.exceptions import APIException

class Conflict(APIException):
    status_code = 409
    default_detail = 'Conflict.'
    default_code = 'conflict'

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None:
        response.data = {
            'error': {
                'code': getattr(exc, '')
            }
        }