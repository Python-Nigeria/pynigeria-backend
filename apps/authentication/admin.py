from django.contrib.admin import ModelAdmin, register

from .models import OTPVerification, User


@register(User)
class UserAdmin(ModelAdmin):
    list_display = [
        "id",
        "email",
        "is_email_verified",
        "is_2fa_enabled",
        "is_superuser",
        "is_staff",
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


@register(OTPVerification)
class OTPVerificationAdmin(ModelAdmin):
    list_display = ["otp", "user", "created_at", "is_used"]
    list_filter = ["user", "created_at", "is_used"]
