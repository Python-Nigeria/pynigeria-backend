from django.db.models.signals import post_save
from django.dispatch import receiver, Signal

from .email import EmailOTP
from .models import User

login_otp_requested = Signal()


@receiver(post_save, sender=User)
def send_otp_email(sender, instance, created, **kwargs):
    """
    This handles sending verification emails to new users after saving.
    """
    try:
        if all([created, not instance.is_superuser, not instance.is_test_user]):
            EmailOTP(instance).send_email()
    except Exception as e:
        raise Exception(str(e))


@receiver(login_otp_requested)
def send_login_otp_email(sender, user, context, **kwargs):
    """
    This handles sending verification emails for logins and resends.
    """
    try:
        if not user.is_superuser:
            EmailOTP(user, context=context).send_email()
    except Exception as e:
        raise Exception(str(e))
