from django.db.models.signals import post_save
from django.dispatch import receiver

from .email import JobNotificationEmail
from .models import Job

@receiver(post_save, sender=Job)
def send_notification(sender, instance, created, **kwargs):
    if instance.version > 1:
        return
    if created:

        try:
            JobNotificationEmail(instance).send_to_admins()
        except Exception as e:
            raise Exception(str(e))
