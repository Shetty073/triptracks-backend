from rest_framework import status
from rest_framework.response import Response
from triptracks.constants import ErrorMessages

def success(data: dict = {}, custom_message: str = None, headers = None):
    res_data = {}
    res_data["data"] = data
    res_data["success"] = True
    res_data["message"] = custom_message or "Operation successful"
    return Response(data=res_data, status=status.HTTP_200_OK, headers=headers)

def success_created(data: dict = {}, custom_message: str = None, headers = None):
    res_data = {}
    res_data["data"] = data
    res_data["success"] = True
    res_data["message"] = custom_message or "Record inserted successfully"
    return Response(data=res_data, status=status.HTTP_201_CREATED, headers=headers)

def success_updated(data: dict = {}, custom_message: str = None, headers = None):
    res_data = {}
    res_data["data"] = data
    res_data["success"] = True
    res_data["message"] = custom_message or "Record updated successfully"
    return Response(data=res_data, status=status.HTTP_202_ACCEPTED, headers=headers)

def bad_request(data: dict = {}, custom_message: str = None, headers = None):
    res_data = {}
    res_data["data"] = data
    res_data["success"] = True
    res_data["message"] = custom_message or ErrorMessages.get(status.HTTP_400_BAD_REQUEST)
    return Response(data=res_data, status=status.HTTP_400_BAD_REQUEST, headers=headers)

def not_authenticated(data: dict = {}, custom_message: str = None, headers = None):
    res_data = {}
    res_data["data"] = data
    res_data["success"] = True
    res_data["message"] = custom_message or ErrorMessages.get(status.HTTP_401_UNAUTHORIZED)
    return Response(data=res_data, status=status.HTTP_401_UNAUTHORIZED, headers=headers)

def payment_required(data: dict = {}, custom_message: str = None, headers = None):
    res_data = {}
    res_data["data"] = data
    res_data["success"] = True
    res_data["message"] = custom_message or ErrorMessages.get(status.HTTP_402_PAYMENT_REQUIRED)
    return Response(data=res_data, status=status.HTTP_402_PAYMENT_REQUIRED, headers=headers)

def forbidden(data: dict = {}, custom_message: str = None, headers = None):
    res_data = {}
    res_data["data"] = data
    res_data["success"] = True
    res_data["message"] = custom_message or ErrorMessages.get(status.HTTP_403_FORBIDDEN)
    return Response(data=res_data, status=status.HTTP_403_FORBIDDEN, headers=headers)

def not_found(data: dict = {}, custom_message: str = None, headers = None):
    res_data = {}
    res_data["data"] = data
    res_data["success"] = True
    res_data["message"] = custom_message or ErrorMessages.get(status.HTTP_404_NOT_FOUND)
    return Response(data=res_data, status=status.HTTP_404_NOT_FOUND, headers=headers)

def method_not_allowed(data: dict = {}, custom_message: str = None, headers = None):
    res_data = {}
    res_data["data"] = data
    res_data["success"] = True
    res_data["message"] = custom_message or ErrorMessages.get(status.HTTP_405_METHOD_NOT_ALLOWED)
    return Response(data=res_data, status=status.HTTP_405_METHOD_NOT_ALLOWED, headers=headers)

def teapot(data: dict = {}, custom_message: str = None, headers = None):
    res_data = {}
    res_data["data"] = data
    res_data["success"] = True
    res_data["message"] = custom_message or ErrorMessages.get(status.HTTP_418_IM_A_TEAPOT)
    return Response(data=res_data, status=status.HTTP_418_IM_A_TEAPOT, headers=headers)

def upgrade_required(data: dict = {}, custom_message: str = None, headers = None):
    res_data = {}
    res_data["data"] = data
    res_data["success"] = True
    res_data["message"] = custom_message or ErrorMessages.get(status.HTTP_426_UPGRADE_REQUIRED)
    return Response(data=res_data, status=status.HTTP_426_UPGRADE_REQUIRED, headers=headers)

def too_many_requests(data: dict = {}, custom_message: str = None, headers = None):
    res_data = {}
    res_data["data"] = data
    res_data["success"] = True
    res_data["message"] = custom_message or ErrorMessages.get(status.HTTP_429_TOO_MANY_REQUESTS)
    return Response(data=res_data, status=status.HTTP_429_TOO_MANY_REQUESTS, headers=headers)

def unavailable_for_legal_reasons(data: dict = {}, custom_message: str = None, headers = None):
    res_data = {}
    res_data["data"] = data
    res_data["success"] = True
    res_data["message"] = custom_message or ErrorMessages.get(status.HTTP_451_UNAVAILABLE_FOR_LEGAL_REASONS)
    return Response(data=res_data, status=status.HTTP_451_UNAVAILABLE_FOR_LEGAL_REASONS, headers=headers)

def internal_server_error(data: dict = {}, custom_message: str = None, headers = None):
    res_data = {}
    res_data["data"] = data
    res_data["success"] = True
    res_data["message"] = custom_message or ErrorMessages.get(status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response(data=res_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR, headers=headers)

def not_implemented(data: dict = {}, custom_message: str = None, headers = None):
    res_data = {}
    res_data["data"] = data
    res_data["success"] = True
    res_data["message"] = custom_message or ErrorMessages.get(status.HTTP_501_NOT_IMPLEMENTED)
    return Response(data=res_data, status=status.HTTP_501_NOT_IMPLEMENTED, headers=headers)

def service_unavailable(data: dict = {}, custom_message: str = None, headers = None):
    res_data = {}
    res_data["data"] = data
    res_data["success"] = True
    res_data["message"] = custom_message or ErrorMessages.get(status.HTTP_503_SERVICE_UNAVAILABLE)
    return Response(data=res_data, status=status.HTTP_503_SERVICE_UNAVAILABLE, headers=headers)
