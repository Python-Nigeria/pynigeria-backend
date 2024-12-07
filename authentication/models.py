from django.contrib.auth.models import (
    BaseUserManager,
    AbstractBaseUser,
    PermissionsMixin,
)
from django.db.models import (
    Model,
    CharField,
    EmailField,
    BooleanField,
    DateTimeField,
    OneToOneField,
    CASCADE,
)
from nanoid import (
    generate,
)  # Ensure 'id' defaults in migration files are set to 'nanoid.generate' and not 'nanoid.generate.generate'
from django.utils import timezone


class UserManager(BaseUserManager):
    """
    Regular users accounts are set up passwordless, only superusers require a password.
    """

    def _create_user(self, **kwargs):
        email = kwargs.pop("email")
        password = kwargs.pop("password", None)
        normalized_email = self.normalize_email(email)
        user = self.model(email=normalized_email, **kwargs)
        if password:
            user.set_password(password)  # For superusers currently
        user.save(using=self._db)
        return user

    def create_superuser(self, **kwargs):
        kwargs.setdefault("is_email_verified", True)
        kwargs.setdefault("is_superuser", True)
        kwargs.setdefault("is_staff", True)
        return self._create_user(**kwargs)

    def create_user(self, **kwargs):
        return self._create_user(**kwargs)


class User(AbstractBaseUser, PermissionsMixin):
    id = CharField(
        max_length=21, primary_key=True, editable=False, unique=True, default=generate
    )
    email = EmailField(max_length=120, blank=False, unique=True, db_index=True)
    is_email_verified = BooleanField(default=False, db_index=True)
    is_superuser = BooleanField(default=False)
    is_staff = BooleanField(default=False)
    is_otp_email_sent = BooleanField(default=False)
    is_test_user = BooleanField(default=False)  # Useful only for running tests
    created = DateTimeField(auto_now_add=True)
    updated = DateTimeField(auto_now=True)
    last_login = DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "email"

    class Meta:
        db_table = "user"
        ordering = ["-created"]

    def __str__(self):
        return self.email


class OTPCode(Model):
    code = CharField(max_length=6, unique=True, db_index=True)
    user = OneToOneField(User, related_name="otp", on_delete=CASCADE)
    expiry = DateTimeField(
        default=timezone.now() + timezone.timedelta(minutes=15),
        editable=False,
        db_index=True,
    )

    class Meta:
        db_table = "user_otp_code"
        ordering = ["-expiry"]

    def __str__(self):
        return f"{self.user.email}'s OTP code"
