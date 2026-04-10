from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Event, RSVP
from .permissions import IsEventOwnerOrAdminDelete
from .serializers import EventCreateSerializer, EventSerializer, RSVPSerializer


class EventListCreateView(generics.ListCreateAPIView):
	permission_classes = [permissions.IsAuthenticatedOrReadOnly]

	def get_queryset(self):
		queryset = Event.objects.annotate(rsvp_count=Count("rsvps"))

		event_type = self.request.query_params.get("event_type")
		is_online = self.request.query_params.get("is_online")
		upcoming = self.request.query_params.get("upcoming")

		now = timezone.now()
		if upcoming is None or upcoming.lower() == "true":
			queryset = queryset.filter(date__gt=now)
		elif upcoming.lower() == "false":
			queryset = queryset

		if event_type:
			queryset = queryset.filter(event_type=event_type)

		if is_online is not None:
			if is_online.lower() == "true":
				queryset = queryset.filter(is_online=True)
			elif is_online.lower() == "false":
				queryset = queryset.filter(is_online=False)

		return queryset


	def get_serializer_class(self):
		if self.request.method == "POST":
			return EventCreateSerializer
		return EventSerializer


	def perform_create(self, serializer):
		serializer.save(created_by=self.request.user)


class EventRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
	queryset = Event.objects.annotate(rsvp_count=Count("rsvps"))
	permission_classes = [IsEventOwnerOrAdminDelete]

	def get_permissions(self):
		if self.request.method in permissions.SAFE_METHODS:
			return [permissions.AllowAny()]
		return [permission() for permission in self.permission_classes]


	def get_serializer_class(self):
		if self.request.method in ["PUT", "PATCH"]:
			return EventCreateSerializer
		return EventSerializer


class RSVPCreateDeleteView(APIView):
	permission_classes = [permissions.IsAuthenticated]

	def post(self, request, pk):
		event = get_object_or_404(Event, pk=pk)
		serializer = RSVPSerializer(
			data={"event": event.id}, context={"request": request}
		)
		serializer.is_valid(raise_exception=True)
		serializer.save(event=event, user=request.user)
		return Response(serializer.data, status=status.HTTP_201_CREATED)


	def delete(self, request, pk):
		event = get_object_or_404(Event, pk=pk)
		rsvp = RSVP.objects.filter(event=event, user=request.user).first()
		if not rsvp:
			return Response(
				{"detail": "You have not RSVPd to this event."},
				status=status.HTTP_404_NOT_FOUND,
			)

		rsvp.delete()
		return Response(status=status.HTTP_204_NO_CONTENT)
