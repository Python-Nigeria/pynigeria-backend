from django.db import IntegrityError
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed, Throttled, ValidationError
from rest_framework.response import Response
from rest_framework.views import exception_handler


def pynigeria_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None:
        response = Response(
            {"detail": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    if isinstance(exc, (ValidationError, AuthenticationFailed, Throttled)):
        data = response.data
        errors = []

        if isinstance(data, dict):
            for field, value in data.items():
                # DRF error values are usually lists of strings/ErrorDetail
                if isinstance(value, list):
                    for v in value:
                        msg = str(v)
                        code = getattr(v, "code", None)
                        if field not in ["detail", "error", "non_field_errors"]:
                            if code == "required":
                                errors.append(f"{field.title()} field is required.")
                            elif code == "blank":
                                errors.append(f"{field.title()} field cannot be blank.")
                            else:
                                errors.append(msg)
                        else:
                            errors.append(msg)
                else:
                    errors.append(str(value))
        elif isinstance(data, list):
            errors = [str(v) for v in data]
        else:
            errors = [str(data)]

        if len(errors) == 1:
            errors = errors[0]

        response.data = {"detail": errors}
        # Ensure status code 429 for Throttling
        if isinstance(exc, Throttled):
            response.status_code = status.HTTP_429_TOO_MANY_REQUESTS
    elif isinstance(exc, IntegrityError):
        response.status_code = status.HTTP_409_CONFLICT
    elif isinstance(exc, Throttled):
        response.status_code = status.HTTP_429_TOO_MANY_REQUESTS

    return response
