from django.db.models.signals import post_save
from django.dispatch import receiver

from .email import EmailOTP
from .models import User


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
