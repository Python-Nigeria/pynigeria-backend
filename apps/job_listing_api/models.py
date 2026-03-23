from django.conf import settings
from django.db import models
from taggit.managers import TaggableManager

# Create your models here.


class JobTypeChoice(models.TextChoices):
    FULL_TIME = "Full Time"
    PART_TIME = "Part Time"
    CONTRACT = "Contract"
    INTERNSHIP = "Internship"
    VOLUNTARY = "Voluntary"


class JobStatus(models.TextChoices):
    DRAFT = "Draft"
    PUBLISHED = "Published"
    ARCHIVED = "Archived"
    EXPIRED = "Expired"


class JobVisibility(models.TextChoices):
    PRIVATE = "Private"
    INTERNAL = "Internal"
    PUBLIC = "Public"
    FEATURED = "Featured"


class SkillLevel(models.TextChoices):
    BEGINNER = "Beginner"
    INTERMIDIATE = "Intermidiate"
    ADVANCED = "Advanced"


class JobBookmarkStatus(models.TextChoices):
    SAVED = "Saved"
    APPLIED = "Applied"
    INTERVIEWING = "Interviewing"
    REJECTED = "Rejected"
    OFFERED = "Offered"
    ARCHIVED = "Archived"





class Company(models.Model):
    name = models.CharField(max_length=255, unique=True)
    location = models.CharField(max_length=255, null=True)
    description = models.TextField(null=True)
    website = models.URLField(max_length=255, null=True)

    def __str__(self) -> str:
        return self.name

class Skill(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self) -> str:
        return self.name
class Job(models.Model):
    company = models.ForeignKey(
        Company, on_delete=models.SET_NULL, null=True, to_field="name"
    )
    company_name = models.CharField(max_length=255)
    job_title = models.CharField(max_length=255)
    job_description = models.TextField()
    skills = models.ManyToManyField(
        Skill,
        related_name="jobs",
        through="JobSkill",
        through_fields=("job", "skill"),
        db_index=True,
    )
    tags = TaggableManager()
    # fields for enhanced functionality
    status = models.CharField(
        max_length=20, choices=JobStatus.choices, default=JobStatus.DRAFT
    )
    visibility = models.CharField(
        max_length=20, choices=JobVisibility.choices, default=JobVisibility.PRIVATE
    )

    # Scheduling and expiry
    published_at = models.DateTimeField(null=True, blank=True)
    application_deadline = models.DateTimeField(null=True)

    employment_type = models.CharField(
        max_length=255, choices=JobTypeChoice.choices, default=JobTypeChoice.FULL_TIME
    )

    salary = models.DecimalField(max_digits=17, decimal_places=2, null=True)

    # Tracking and metrics
    posted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    views_count = models.PositiveIntegerField(default=0)
    applications_count = models.PositiveIntegerField(default=0)

    # Versioning and audit
    original_job = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="revisions",
        db_index=True,
    )
    version = models.IntegerField(default=1)
    # existing fields
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    slug = models.UUIDField(unique=True, db_index=True)

    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.job_title} at {self.company_name}"

    def save(self, *args, **kwargs):
        if self.company_name:
            self.company_name = self.company_name.strip().lower()
        super().save(*args, **kwargs)

    class Meta:
        indexes = [
            models.Index(fields=["original_job", "version"]),  # Composite index
        ]


class JobSkill(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="job_skills")
    skill = models.ForeignKey(
        Skill, on_delete=models.CASCADE, to_field="name"
    )  # References the `name` field of Skill
    skill_level = models.CharField(
        max_length=255, choices=SkillLevel.choices, default=SkillLevel.BEGINNER
    )

    class Meta:
        unique_together = ("job", "skill")

    def __str__(self):
        return f"{self.job.job_title} - {self.skill.name}"


class BookmarkFolder(models.Model):
    """Optional folder organization for job bookmarks"""

    folder_name = models.CharField(max_length=255)
    folder_description = models.TextField(null=True, blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="bookmark_folders",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["user", "folder_name"]
        indexes = [models.Index(fields=["folder_name"])]

    def __str__(self):
        return self.folder_name


class Bookmark(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="job_bookmarks"
    )
    job = models.ForeignKey(
        Job, on_delete=models.CASCADE, related_name="bookmarks"  # Your Job model
    )
    folder = models.ForeignKey(
        BookmarkFolder,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="bookmarks",
    )

    # Bookmark metadata
    status = models.CharField(
        max_length=20,
        choices=JobBookmarkStatus.choices,
        default=JobBookmarkStatus.SAVED,
    )
    notes = models.TextField(blank=True, null=True)

    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["user", "job"]  # Prevent duplicate bookmarks
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.user.email} bookmarked this job"
