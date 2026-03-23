from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from taggit.managers import TaggableManager

# Create your models here.


User = settings.AUTH_USER_MODEL


class PublishManager(models.Manager):
    def get_queryset(self):
        """
        Returns a queryset of approved uploads.
        """
        return super().get_queryset().filter(status="APPROVED")


class UserUpload(models.Model):

    tags = TaggableManager()

    UPLOAD_TYPE = [
        ("PDF", "PDF Document"),
        ("EBOOK", "Ebook"),
        ("IMAGE", "image"),
    ]

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"

    def validate_file_extension(value):
        """
        Validates the file extension of the given file.
        """
        allowed_files = ["pdf", "doc", "docx", "jpg", "jpeg", "png"]
        file_extension = value.name.split(".")[-1].lower()
        if file_extension not in allowed_files:
            raise ValidationError(
                f'Unsupported file type. Allowed types: {", ".join(allowed_files)}'
            )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="uploads")
    upload_type = models.CharField(max_length=10, choices=UPLOAD_TYPE)
    file = models.FileField(
        upload_to="uploads/%Y/%m/%d/", validators=[validate_file_extension]
    )
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    published_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.PENDING
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at"]),
        ]

    published = PublishManager()
    objects = models.Manager()

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at"]),
        ]

    def __str__(self):
        """
        Returns a string representation of the UserUpload instance,
        including the username, upload type, and file name.
        """
        return f"{self.user.username} - {self.upload_type} - {self.file.name}"

    def update_file_status(self, new_status):
        """
        Updates the status of the file.

        The possible status transitions are:
          PENDING -> APPROVED or REJECTED
          APPROVED -> None
          REJECTED -> None
        """
        valid_status = {
            self.Status.PENDING: [self.Status.APPROVED, self.Status.REJECTED],
            self.Status.APPROVED: [],
            self.Status.REJECTED: [],
        }

        if new_status not in valid_status[self.status]:
            raise ValidationError(
                f"Cannot change status from {self.status} to {new_status}"
            )

        if new_status == self.Status.REJECTED:
            self.file.delete()

        self.status = new_status
        self.save()
