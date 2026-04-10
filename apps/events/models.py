from django.conf import settings
from django.db import models


class EventType(models.TextChoices):
	WEBINAR = "webinar", "Webinar"
	HACKATHON = "hackathon", "Hackathon"
	MEETUP = "meetup", "Meetup"
	WORKSHOP = "workshop", "Workshop"
	CODING_SESSION = "coding_session", "Coding Session"
	CONFERENCE = "conference", "Conference"
	OTHER = "other", "Other"


class Event(models.Model):
	title = models.CharField(max_length=255)
	description = models.TextField()
	date = models.DateTimeField()
	location = models.CharField(max_length=255, blank=True)
	is_online = models.BooleanField(default=False)
	link = models.URLField(blank=True, null=True)
	event_type = models.CharField(max_length=30, choices=EventType.choices)
	created_by = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name="events",
	)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ["date", "-created_at"]

	def __str__(self):
		return self.title


class RSVP(models.Model):
	event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="rsvps")
	user = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name="rsvps",
	)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		unique_together = ("event", "user")
		ordering = ["-created_at"]

	def __str__(self):
		return f"{self.user} - {self.event}"
