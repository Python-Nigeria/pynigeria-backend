from base64 import b32encode

from django.conf import settings
from django.core import signing
from django.db import transaction
from django.utils.dateformat import format
from django_otp.plugins.otp_totp.models import TOTPDevice
from pyotp import TOTP
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.serializers import (
    BooleanField,
    CharField,
    EmailField,
    ModelSerializer,
    Serializer,
    SerializerMethodField,
    ValidationError,
)
from rest_framework_simplejwt.tokens import RefreshToken

from .email import EmailOTP
from .models import OTPCode, User


class UserSerializer(ModelSerializer):
    created = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "is_email_verified",
            "is_2fa_enabled",
            "auth_provider",
            "created",
        )
        read_only_fields = (
            "id",
            "email",
            "is_email_verified",
            "is_2fa_enabled",
            "auth_provider",
            "created",
        )

    def get_created(self, obj):
        return format(obj.created, "M d, Y. P")


class TOTPDeviceSerializer(ModelSerializer):
    class Meta:
        model = TOTPDevice
        fields = ["user", "name", "confirmed"]


# ─── Registration ────────────────────────────────────────────────────────────


class RegisterSerializer(Serializer):
    id = CharField(read_only=True)
    email = EmailField()
    password = CharField(write_only=True, min_length=8)
    is_email_verified = BooleanField(read_only=True)
    message = CharField(read_only=True)

    def validate(self, data):
        if User.objects.filter(email=data.get("email")).exists():
            raise ValidationError(
                detail={"error": "An account with this email already exists."}
            )
        return data

    def save(self, **kwargs):
        return User.objects.create_user(
            email=self.validated_data["email"],
            password=self.validated_data["password"],
            auth_provider="password",
        )

    def to_representation(self, instance):
        user_data = UserSerializer(instance).data
        user_data["message"] = (
            "Account created. Check your email to verify your account."
        )
        return user_data


# ─── Email Verification ───────────────────────────────────────────────────────


class EmailVerifyBeginSerializer(Serializer):
    email = EmailField(write_only=True)
    message = CharField(read_only=True)

    def validate(self, data):
        email = data.get("email")
        self.user = User.objects.select_related("otp").filter(email=email).first()
        if not self.user:
            raise ValidationError(
                detail={"error": "No existing account is associated with this email."}
            )
        if self.user.is_email_verified:
            raise ValidationError(
                detail={"error": "This account has already been verified."}
            )
        # Prevent spamming — only block if a valid unexpired OTP already exists
        if hasattr(self.user, "otp") and not self.user.otp.is_expired:
            raise ValidationError(
                detail={
                    "error": "A verification link was already sent. Check your email."
                }
            )
        return data

    def save(self, **kwargs):
        EmailOTP(self.user).send_email()
        return "Check your email for a verification link."

    def to_representation(self, instance):
        return {"message": instance}


class EmailVerifyCompleteSerializer(Serializer):
    id = CharField(read_only=True)
    email = EmailField(read_only=True)
    is_email_verified = BooleanField(read_only=True)
    message = CharField(read_only=True)

    def validate(self, data):
        token = self.context.get("token")
        try:
            otp_data = signing.loads(token, key=settings.SECRET_KEY)
        except signing.BadSignature:
            raise ValidationError(detail={"error": "Invalid verification token."})

        self.otp = (
            OTPCode.objects.select_related("user")
            .filter(code=otp_data[0], user_id=otp_data[1])
            .first()
        )
        if not self.otp:
            raise ValidationError(detail={"error": "OTP code does not exist."})

        self.user = self.otp.user

        if self.otp.is_expired:
            with transaction.atomic():
                self.otp.delete()
                EmailOTP(self.user).send_email()
            raise ValidationError(
                detail={"error": "Link expired. A new verification link has been sent."}
            )
        return data

    def save(self, **kwargs):
        with transaction.atomic():
            self.user.is_email_verified = True
            self.user.save()
            self.otp.delete()
        return self.user

    def to_representation(self, instance):
        user_data = UserSerializer(instance).data
        user_data.pop("created", None)
        user_data["message"] = "Email verified successfully. You can now log in."
        return user_data


# ─── Login ────────────────────────────────────────────────────────────────────


class LoginSerializer(Serializer):
    """
    Step 1 of login — always requires email + password.
    If the user has 2FA enabled, returns a flag telling the frontend
    to prompt for the TOTP code next. Otherwise issues tokens immediately.
    """

    email = EmailField()
    password = CharField(write_only=True)
    id = CharField(read_only=True)
    access = CharField(read_only=True)
    refresh = CharField(read_only=True)
    requires_2fa = BooleanField(read_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        self.user = User.objects.filter(email=email).first()

        if not self.user:
            raise ValidationError(
                detail={"error": "No account is associated with this email."}
            )
        if not self.user.is_email_verified:
            raise ValidationError(
                detail={"error": "Please verify your email before logging in."}
            )
        if not self.user.has_usable_password():
            # Social login user trying to use password — guide them correctly
            raise ValidationError(
                detail={
                    "error": f"This account was created via {self.user.auth_provider}. Please use that to log in."
                }
            )
        if not self.user.check_password(password):
            raise AuthenticationFailed("Incorrect email or password.")

        return data

    def save(self, **kwargs):
        # If 2FA is on, don't issue tokens yet — frontend will call LoginTOTPSerializer next
        if self.user.has_active_2fa:
            self.validated_data.clear()
            self.validated_data["requires_2fa"] = True
            self.validated_data["email"] = self.user.email
            return self.validated_data

        # No 2FA — issue tokens immediately
        return self._issue_tokens()

    def _issue_tokens(self):
        refresh_token = RefreshToken.for_user(self.user)
        self.validated_data.clear()
        self.validated_data["id"] = self.user.id
        self.validated_data["email"] = self.user.email
        self.validated_data["access"] = str(refresh_token.access_token)
        self.validated_data["refresh"] = str(refresh_token)
        self.validated_data["requires_2fa"] = False
        return self.validated_data

    def to_representation(self, instance):
        return instance


class LoginTOTPSerializer(Serializer):
    """
    Step 2 of login — only called if LoginSerializer returned requires_2fa=True.
    Verifies the TOTP code and then issues tokens.
    """

    email = EmailField()
    otp_token = CharField(write_only=True)
    id = CharField(read_only=True)
    access = CharField(read_only=True)
    refresh = CharField(read_only=True)

    def validate(self, data):
        email = data.get("email")
        otp_token = data.get("otp_token")

        self.user = User.objects.filter(email=email).first()
        if not self.user:
            raise ValidationError(
                detail={"error": "No account is associated with this email."}
            )

        self.device = (
            TOTPDevice.objects.select_related("user")
            .filter(user=self.user, confirmed=True)
            .first()
        )
        if not self.device:
            raise ValidationError(
                detail={"error": "No confirmed 2FA device found for this account."}
            )

        secret_key = b32encode(self.device.bin_key).decode()
        if not TOTP(secret_key).verify(otp_token):
            raise ValidationError(detail={"error": "Invalid or expired TOTP code."})

        return data

    def save(self, **kwargs):
        refresh_token = RefreshToken.for_user(self.user)
        self.validated_data.clear()
        self.validated_data["id"] = self.user.id
        self.validated_data["email"] = self.user.email
        self.validated_data["access"] = str(refresh_token.access_token)
        self.validated_data["refresh"] = str(refresh_token)
        return self.validated_data

    def to_representation(self, instance):
        return instance


# ─── Optional 2FA Setup (from settings page) ─────────────────────────────────


class TOTPDeviceCreateSerializer(Serializer):
    """Called when an already-logged-in user chooses to enable 2FA from settings."""

    user = CharField(read_only=True)
    name = CharField(read_only=True)
    confirmed = BooleanField(read_only=True, default=False)

    def validate(self, data):
        # User comes from request context, not request body — they're already authenticated
        self.user = self.context["request"].user
        if not self.user.is_email_verified:
            raise ValidationError(
                detail={"error": "Please verify your email before enabling 2FA."}
            )
        if TOTPDevice.objects.filter(user=self.user, confirmed=True).exists():
            raise ValidationError(
                detail={"error": "A 2FA device is already active on this account."}
            )
        return data

    def save(self, **kwargs):
        # Delete any previous unconfirmed device before creating a new one
        TOTPDevice.objects.filter(user=self.user, confirmed=False).delete()
        return TOTPDevice.objects.create(
            user=self.user, name=self.user.email, confirmed=False
        )

    def to_representation(self, instance):
        return TOTPDeviceSerializer(instance).data


class QRCodeDataSerializer(Serializer):
    """Returns the otpauth:// URL used to generate the QR code."""

    otpauth_url = CharField(read_only=True)

    def validate(self, data):
        self.user = self.context["request"].user
        self.device = TOTPDevice.objects.filter(user=self.user, confirmed=False).first()
        if not self.device:
            raise ValidationError(
                detail={
                    "error": "No pending 2FA setup found. Please start 2FA setup first."
                }
            )
        return data

    def save(self, **kwargs):
        return self.device.config_url


class VerifyTOTPDeviceSerializer(Serializer):
    """Confirms the TOTP device after the user scans the QR code and enters their first code."""

    otp_token = CharField(write_only=True)
    confirmed = BooleanField(read_only=True)
    message = CharField(read_only=True)

    def validate(self, data):
        self.user = self.context["request"].user
        self.device = TOTPDevice.objects.filter(user=self.user, confirmed=False).first()
        if not self.device:
            raise ValidationError(
                detail={"error": "No pending 2FA device found for this account."}
            )
        secret_key = b32encode(self.device.bin_key).decode()
        if not TOTP(secret_key).verify(data.get("otp_token")):
            raise ValidationError(detail={"error": "Invalid TOTP code. Try again."})
        return data

    def save(self, **kwargs):
        with transaction.atomic():
            self.device.confirmed = True
            self.device.save()
            self.user.is_2fa_enabled = True
            self.user.save()
        return self.device

    def to_representation(self, instance):
        result = TOTPDeviceSerializer(instance).data
        result["message"] = "2FA enabled successfully."
        return result
