from django.contrib import admin

from .models import Event, RSVP


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
	list_display = ("title", "event_type", "date", "is_online", "created_by")
	list_filter = ("event_type", "is_online", "date")
	search_fields = ("title", "description", "location", "created_by__email")


@admin.register(RSVP)
class RSVPAdmin(admin.ModelAdmin):
	list_display = ("event", "user", "created_at")
	list_filter = ("created_at",)
	search_fields = ("event__title", "user__email")
