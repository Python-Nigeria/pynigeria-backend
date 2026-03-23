from django.contrib.admin import ModelAdmin, register

from .models import OTPCode, User


@register(User)
class UserAdmin(ModelAdmin):
    list_display = [
        "id",
        "email",
        "is_email_verified",
        "is_2fa_enabled",
        "is_superuser",
        "is_staff",
        # "is_otp_email_sent",
        "created",
        "updated",
        "last_login",
    ]

    readonly_fields = ["password"]

    list_filter = [
        "id",
        "email",
        "is_email_verified",
        "is_2fa_enabled",
        "is_superuser",
        "is_staff",
        "created",
    ]


@register(OTPCode)
class OTPCodeAdmin(ModelAdmin):
    list_display = ["code", "user", "expiry"]
    list_filter = ["user", "expiry"]
