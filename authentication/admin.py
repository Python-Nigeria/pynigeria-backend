from django.contrib.admin import register, ModelAdmin
from .models import User, OTPCode


@register(User)
class UserAdmin(ModelAdmin):
    list_display = [
        "id",
        "email",
        "is_email_verified",
        "is_superuser",
        "is_staff",
        "is_otp_email_sent",
        "created",
        "updated",
        "last_login",
    ]

    list_filter = [
        "id",
        "email",
        "is_email_verified",
        "is_superuser",
        "is_staff",
        "created",
    ]


@register(OTPCode)
class OTPCodeAdmin(ModelAdmin):
    list_display = ["code", "user", "expiry"]
    list_filter = ["user", "expiry"]
