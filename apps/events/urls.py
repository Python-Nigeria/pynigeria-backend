from django.urls import path

from .views import EventListCreateView, EventRetrieveUpdateDeleteView, RSVPCreateDeleteView

urlpatterns = [
	path("", EventListCreateView.as_view(), name="event-list"),
	path("<int:pk>/", EventRetrieveUpdateDeleteView.as_view(), name="event-detail"),
	path("<int:pk>/rsvp/", RSVPCreateDeleteView.as_view(), name="event-rsvp"),
]
