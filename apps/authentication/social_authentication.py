from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from .signals import login_otp_requested
from social_core.utils import (
    partial_pipeline_data,
    user_is_active,
    user_is_authenticated,
)


def complete_social_authentication(request, backend):
    backend = request.backend
    user = request.user

    # Only pass user into pipeline if already authenticated
    is_user_authenticated = user_is_authenticated(user)
    user = user if is_user_authenticated else None

    # Resume a partial pipeline (e.g. user was mid-way through OAuth) or start fresh
    partial = partial_pipeline_data(backend, user)
    if partial:
        user = backend.continue_pipeline(partial)
        backend.clean_partial_pipeline(partial.token)
    else:
        user = backend.complete(user=user)

    # Ensure the pipeline returned an actual User instance, not a redirect or None
    user_model = backend.strategy.storage.user.user_model()
    if user and not isinstance(user, user_model):
        raise AuthenticationFailed("Social login did not return a valid user.")

    if not user:
        raise AuthenticationFailed("Social authentication failed. Please try again.")

    if not user_is_active(user):
        raise AuthenticationFailed("This account has been deactivated.")

    is_new = getattr(user, "is_new", False)

    # Trigger OTP flow instead of issuing tokens directly
    # This applies to both existing and new social users to satisfy the strict OTP requirement.
    context = "signup" if is_new else "login"
    login_otp_requested.send(
        sender=complete_social_authentication, user=user, context=context
    )

    return Response(
        {
            "data": {
                "requires_email_otp": True,
                "email": user.email,
                "message": "OTP sent to your email. Please verify to continue.",
            }
        },
        status=status.HTTP_200_OK if not is_new else status.HTTP_201_CREATED,
    )
