from rest_framework.serializers import (
    ModelSerializer,
    Serializer,
    CharField,
    EmailField,
    BooleanField,
    ValidationError,
    SerializerMethodField,
)
from .models import User, OTPCode
from django.db import IntegrityError, transaction
from django.utils.dateformat import format
from django.core import signing
from django.utils import timezone
from .email import EmailOTP
from django.conf import settings


class UserSerializer(ModelSerializer):
    created = SerializerMethodField()

    class Meta:
        model = User
        fields = ("id", "email", "is_email_verified", "created")
        read_only_fields = ("id", "email", "is_email_verified", "created")

    def get_created(self, obj):
        return format(obj.created, "M d, Y. P")


class RegisterSerializer(Serializer):
    id = CharField(read_only=True)
    email = EmailField()
    is_email_verified = BooleanField(read_only=True)
    message = CharField(read_only=True)

    def validate(self, data):
        email = data.get("email", None)
        if User.objects.filter(email=email).exists():
            raise IntegrityError("An account with this email already exists.")
        return data

    def save(self, **kwargs):
        return User.objects.create_user(**self.validated_data)

    def to_representation(self, instance):
        user_data = UserSerializer(instance).data
        user_data["message"] = "Check your email for a verification link."
        return user_data


class EmailVerifyBeginSerializer(Serializer):
    email = EmailField(write_only=True)
    message = CharField(read_only=True)

    def validate(self, data):
        email = data.get("email", None)
        self.user = User.objects.select_related("otp").filter(email=email).first()
        if not self.user:
            raise ValidationError(
                detail={"error": "No existing account is associated with this email."}
            )
        elif self.user.is_email_verified:
            raise ValidationError(
                detail={"error": "This user account has already been verified."}
            )
        elif self.user.is_otp_email_sent and timezone.now() < self.user.otp.expiry:
            raise ValidationError(
                detail={
                    "error": "Check your email for an already existing verification link."
                }
            )
        return data

    def save(self, **kwargs):
        EmailOTP(self.user).send_email()
        return "Check your email for a verification link."

    def to_representation(self, instance):
        instance = {"message": instance}
        return instance


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
            raise ValidationError(detail={"error": "Invalid OTP code detected."})
        self.otp = (
            OTPCode.objects.select_related("user")
            .filter(code=otp_data[0], user_id=otp_data[1])
            .first()
        )
        if not self.otp:
            raise ValidationError(detail={"error": "OTP code does not exist."})
        self.user = self.otp.user
        if timezone.now() > self.otp.expiry:
            with transaction.atomic():
                self.otp.delete()
                self.user.is_otp_email_sent = False
                self.user.save()
                EmailOTP(self.user).send_email()
                raise ValidationError(
                    detail={
                        "error": "OTP code has expired. A new verification link has been sent to your email."
                    }
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
        user_data.pop("created")
        user_data["message"] = (
            "Your email has been verified successfully. Proceed to 2FA setup."
        )
        return user_data
