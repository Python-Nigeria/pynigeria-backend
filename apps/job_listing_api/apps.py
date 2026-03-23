from django.apps import AppConfig


class JobApiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.job_listing_api"
    verbose_name = "Job Listing"

    def ready(self) -> None:
        from . import signals
