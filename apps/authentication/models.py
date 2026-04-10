from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db.models import (
    CASCADE,
    BooleanField,
    CharField,
    DateTimeField,
    EmailField,
    ForeignKey,
    Model,
)
from django.utils import timezone
from nanoid import generate


def generate_user_id():
    return generate()


class UserManager(BaseUserManager):
    """
    Users authenticate via password (primary) or social login.
    Social login users get an unusable password set automatically.
    Superusers always require a password.
    """

    def _create_user(self, email, password=None, **kwargs):
        if not email:
            raise ValueError("Email is required.")
        normalized_email = self.normalize_email(email)
        user = self.model(email=normalized_email, **kwargs)
        if password:
            user.set_password(password)
        else:
            # Social login users can't log in via password — this is intentional
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **kwargs):
        kwargs.setdefault("is_staff", False)
        kwargs.setdefault("is_superuser", False)
        return self._create_user(email, password, **kwargs)

    def create_superuser(self, email, password, **kwargs):
        if not password:
            raise ValueError("Superusers must have a password.")
        kwargs.setdefault("is_email_verified", True)
        kwargs.setdefault("is_superuser", True)
        kwargs.setdefault("is_staff", True)
        return self._create_user(email, password, **kwargs)


class User(AbstractBaseUser, PermissionsMixin):
    id = CharField(
        max_length=21,
        primary_key=True,
        editable=False,
        unique=True,
        default=generate_user_id,
    )
    email = EmailField(max_length=120, blank=False, unique=True, db_index=True)

    # Tracks how the user signed up: "password", "google", "github", etc.
    # Critical once you have social login — lets you know which provider to redirect to
    auth_provider = CharField(max_length=50, default="password", db_index=True)

    is_email_verified = BooleanField(default=False, db_index=True)

    # Off by default — user opts in from their settings page
    is_2fa_enabled = BooleanField(default=False, db_index=True)

    is_superuser = BooleanField(default=False)
    is_staff = BooleanField(default=False)
    is_test_user = BooleanField(default=False)

    created = DateTimeField(auto_now_add=True)
    updated = DateTimeField(auto_now=True)
    # null=True because new users won't have a last_login until their first login
    # auto_now=True was wrong — Django's auth system manages this field itself
    last_login = DateTimeField(null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        db_table = "user"
        ordering = ["-created"]

    def __str__(self):
        return self.email

    @property
    def has_password(self):
        """Check if user can log in with a password (False for social login users)."""
        return self.has_usable_password()

    @property
    def has_active_2fa(self):
        """True only if 2FA is toggled on AND a confirmed TOTP device exists."""
        return (
            self.is_2fa_enabled
            and hasattr(self, "totp_device")
            and self.totp_device.confirmed
        )


class OTPVerification(Model):
    """
    Short-lived 6-digit code sent to the user's email.
    Used for: email verification on signup, and as the 2FA step if user has no TOTP device.
    """

    user = ForeignKey(User, related_name="otps", on_delete=CASCADE)
    otp = CharField(max_length=6, db_index=True)
    created_at = DateTimeField(auto_now_add=True)
    is_used = BooleanField(default=False)

    class Meta:
        db_table = "user_otp_verification"
        ordering = ["-created_at"]

    def is_expired(self,signup=False):
        if signup: #otp should expired in 24hrs if it is signup
            expiry_time = timezone.timedelta(hours=24)
        else:
            expiry_time = timezone.timedelta(minutes=10) #otp should expired in 10minutes if it is login
        expiry = self.created_at + expiry_time
        return timezone.now() > expiry

    def __str__(self):
        return f"{self.user.email}'s OTP code"
