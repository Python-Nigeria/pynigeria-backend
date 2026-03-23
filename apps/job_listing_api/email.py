from datetime import datetime

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

User = get_user_model()


class JobNotificationEmail:
    def __init__(self, job_instance):
        """
        Initialize with the job instance and recipient email.
        """
        self.job_instance = job_instance

    def __send_to_email(self, subject, recipient_list, context):
        html_message = render_to_string("email.html", context)
        with open("templates/dump.html", "w") as file:
            file.write(html_message)
        plain_message = strip_tags(html_message)

        # Send the email
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            html_message=html_message,
        )

    def send_to_admins(self):
        """
        Send an email notification to all admins when a job is created.
        """
        admins_email = [
            admin.email
            for admin in User.objects.filter(is_staff=True, is_email_verified=True)
        ]
        if not admins_email:
            return
        context = {
            "email_title": "New Job Created",
            "user_name": "Admin",
            "email_message": f"A new job titled {self.job_instance.job_title.title()} has been created.",
            "job_link": f"{settings.CURRENT_ORIGIN}/admin/job_listing_api/job/{self.job_instance.id}/",
        }

        self.__send_to_email("New Job Created", admins_email, context)

    def send_to_poster(self, approved=True, message=None):
        job_status = "approved" if approved else "rejected"
        context = {
            "email_title": f"Your Job Has Been {job_status.capitalize()}",
            "user_name": self.job_instance.posted_by.email,
            "email_message": f"Your job titled {self.job_instance.job_title.title()} has been {job_status}. ",
            "additional_message": message,
            "contact_support": f"to contact support",
            "job_link": f"{settings.CURRENT_ORIGIN}/admin/job_listing_api/job/{self.job_instance.id}/",
            "year": datetime.now().strftime("%Y"),
        }
        self.__send_to_email(
            f"Job {job_status.capitalize()}",
            [self.job_instance.posted_by.email],
            context,
        )
