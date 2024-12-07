from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, Throttled
from django.db import IntegrityError
from rest_framework import status


def pynigeria_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None:
        response = Response(
            {"detail": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    if isinstance(exc, (ValidationError)):
        error_list = []
        try:
            for key, value in exc.get_full_details().items():
                try:
                    for error in value:
                        if error["code"] == "required":
                            error_list.append(f"{key.title()} field is required.")
                        elif error["code"] == "blank":
                            error_list.append(f"{key.title()} field cannot be blank.")
                        elif error["code"] == "unique":
                            error_list.append(error["message"].capitalize())
                        elif error["code"] == "invalid_choice":
                            error_list.append(error["message"])
                        elif error["code"] == "invalid":
                            error_list.append(error["message"].capitalize())
                        else:
                            error_list.append(error)
                except:
                    error_list.append(value["message"])
            if len(error_list) == 1:
                error_list = error_list[0]

            response.data = {"detail": error_list}
        except:
            try:
                response.data = {"detail": str(exc.detail["messages"][0]["message"])}
            except:
                response.data = {"detail": str(exc.detail)}
        response.status_code = status.HTTP_400_BAD_REQUEST
    elif isinstance(exc, IntegrityError):
        response.status_code = status.HTTP_409_CONFLICT
    elif isinstance(exc, Throttled):
        response.status_code = status.HTTP_429_TOO_MANY_REQUESTS

    return response
