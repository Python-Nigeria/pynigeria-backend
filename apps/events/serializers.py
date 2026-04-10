from rest_framework import serializers

from .models import Event, RSVP


class EventSerializer(serializers.ModelSerializer):
	rsvp_count = serializers.IntegerField(read_only=True)

	class Meta:
		model = Event
		fields = [
			"id",
			"title",
			"description",
			"date",
			"location",
			"is_online",
			"link",
			"event_type",
			"created_by",
			"rsvp_count",
			"created_at",
			"updated_at",
		]
		read_only_fields = ["id", "created_by", "rsvp_count", "created_at", "updated_at"]


class EventCreateSerializer(serializers.ModelSerializer):
	class Meta:
		model = Event
		fields = [
			"id",
			"title",
			"description",
			"date",
			"location",
			"is_online",
			"link",
			"event_type",
			"created_by",
			"created_at",
			"updated_at",
		]
		read_only_fields = ["id", "created_by", "created_at", "updated_at"]


class RSVPSerializer(serializers.ModelSerializer):
	class Meta:
		model = RSVP
		fields = ["id", "event", "user", "created_at"]
		read_only_fields = ["id", "user", "created_at"]

	def validate(self, attrs):
		request = self.context.get("request")
		event = attrs.get("event")
		if request and request.user and RSVP.objects.filter(event=event, user=request.user).exists():
			raise serializers.ValidationError(
				{"detail": "You have already RSVPd to this event."}
			)
		return attrs
