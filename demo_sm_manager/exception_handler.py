from rest_framework.views import exception_handler
from rest_framework import status
from user.utils import ResponseHandler
from django.http import JsonResponse

def default_exception_handler(exc, context):
    request = context["request"]
    response = exception_handler(exc, context)
    if not response:
        resp = ResponseHandler.handle_internal_error()   
        response = JsonResponse(resp, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return response