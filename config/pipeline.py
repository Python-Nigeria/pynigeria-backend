from rest_framework.exceptions import AuthenticationFailed
from social_core.pipeline.user import USER_FIELDS


def custom_create_user(backend, details, user=None, *args, **kwargs):
    # Check for existing user with verified email
    if user:
        if not user.is_email_verified:
            raise AuthenticationFailed(
                "This account has not been verified. Check your email for a verification link."
            )
        else:
            return {"is_new": False}  # existing user account
    fields = {
        name: kwargs.get(name, details.get(name))
        for name in backend.setting("USER_FIELDS", USER_FIELDS)
    }
    if not fields:
        return
    fields["is_email_verified"] = True
    user = backend.strategy.create_user(**fields)
    return {"is_new": True, "user": user}
