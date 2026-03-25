from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from social_core.utils import (
    partial_pipeline_data,
    user_is_active,
    user_is_authenticated,
)

from .serializers import UserSerializer


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

    if is_new:
        # New social login user — account just created, send them to verify email or straight to app
        # No password or 2FA setup needed for social users
        user_data = UserSerializer(user).data
        user_data["message"] = "Account created. Welcome!"
        return Response({"data": user_data}, status=status.HTTP_201_CREATED)

    # Returning social login user — issue tokens directly
    # Social providers (Google etc.) handle their own auth security
    # so we don't gate on our internal 2FA flag here
    return _issue_tokens(user)


def _issue_tokens(user):
    """Issue JWT access + refresh tokens for the given user."""
    refresh_token = RefreshToken.for_user(user)
    return Response(
        {
            "data": {
                "id": user.id,
                "email": user.email,
                "access": str(refresh_token.access_token),
                "refresh": str(refresh_token),
                # Tell the frontend which provider this user logged in with
                "auth_provider": user.auth_provider,
                # Let the frontend know if this user has opted into 2FA
                # so it can show the right UI in settings
                "is_2fa_enabled": user.is_2fa_enabled,
            }
        },
        status=status.HTTP_200_OK,
    )
