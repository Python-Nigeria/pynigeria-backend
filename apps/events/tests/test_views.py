from datetime import timedelta

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITransactionTestCase

from apps.authentication.models import User
from apps.events.models import Event, EventType, RSVP


class EventViewTests(APITransactionTestCase):
	def setUp(self):
		self.owner = User.objects.create_user(
			email="owner@example.com", password="testpass123"
		)
		self.other_user = User.objects.create_user(
			email="other@example.com", password="testpass123"
		)
		self.admin = User.objects.create_superuser(
			email="admin@example.com", password="testpass123"
		)

		self.future_event = Event.objects.create(
			title="Future Webinar",
			description="Future event",
			date=timezone.now() + timedelta(days=2),
			location="",
			is_online=True,
			link="https://example.com/event",
			event_type=EventType.WEBINAR,
			created_by=self.owner,
		)
		self.past_event = Event.objects.create(
			title="Past Meetup",
			description="Past event",
			date=timezone.now() - timedelta(days=2),
			location="Lagos",
			is_online=False,
			event_type=EventType.MEETUP,
			created_by=self.owner,
		)

		self.list_url = reverse("event-list")
		self.detail_url = reverse("event-detail", kwargs={"pk": self.future_event.id})

	def test_anyone_can_list_events(self):
		response = self.client.get(self.list_url)
		self.assertEqual(response.status_code, status.HTTP_200_OK)

	def test_list_returns_only_upcoming_events_by_default(self):
		response = self.client.get(self.list_url)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		returned_ids = [item["id"] for item in response.data]
		self.assertIn(self.future_event.id, returned_ids)
		self.assertNotIn(self.past_event.id, returned_ids)

	def test_anyone_can_retrieve_single_event(self):
		response = self.client.get(self.detail_url)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data["id"], self.future_event.id)

	def test_authenticated_user_can_create_event(self):
		self.client.force_authenticate(user=self.owner)
		payload = {
			"title": "New Event",
			"description": "Event description",
			"date": (timezone.now() + timedelta(days=5)).isoformat(),
			"location": "Abuja",
			"is_online": False,
			"event_type": EventType.WORKSHOP,
		}
		response = self.client.post(self.list_url, data=payload, format="json")
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		created = Event.objects.get(id=response.data["id"])
		self.assertEqual(created.created_by, self.owner)

	def test_unauthenticated_user_cannot_create_event(self):
		payload = {
			"title": "Blocked Event",
			"description": "Event description",
			"date": (timezone.now() + timedelta(days=5)).isoformat(),
			"event_type": EventType.OTHER,
		}
		response = self.client.post(self.list_url, data=payload, format="json")
		self.assertIn(
			response.status_code,
			[status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN],
		)

	def test_event_owner_can_update_event(self):
		self.client.force_authenticate(user=self.owner)
		payload = {
			"title": "Updated Future Webinar",
			"description": self.future_event.description,
			"date": self.future_event.date.isoformat(),
			"location": self.future_event.location,
			"is_online": self.future_event.is_online,
			"link": self.future_event.link,
			"event_type": self.future_event.event_type,
		}
		response = self.client.put(self.detail_url, data=payload, format="json")
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.future_event.refresh_from_db()
		self.assertEqual(self.future_event.title, "Updated Future Webinar")

	def test_non_owner_gets_403_when_trying_to_update(self):
		self.client.force_authenticate(user=self.other_user)
		payload = {
			"title": "Unauthorized Update",
			"description": self.future_event.description,
			"date": self.future_event.date.isoformat(),
			"location": self.future_event.location,
			"is_online": self.future_event.is_online,
			"link": self.future_event.link,
			"event_type": self.future_event.event_type,
		}
		response = self.client.put(self.detail_url, data=payload, format="json")
		self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

	def test_event_owner_can_delete_event(self):
		self.client.force_authenticate(user=self.owner)
		response = self.client.delete(self.detail_url)
		self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
		self.assertFalse(Event.objects.filter(id=self.future_event.id).exists())

	def test_non_owner_gets_403_when_trying_to_delete(self):
		self.client.force_authenticate(user=self.other_user)
		response = self.client.delete(self.detail_url)
		self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

	def test_admin_can_delete_event(self):
		self.client.force_authenticate(user=self.admin)
		response = self.client.delete(self.detail_url)
		self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

	def test_event_type_filter_works_correctly(self):
		response = self.client.get(self.list_url, {"event_type": EventType.WEBINAR})
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(len(response.data), 1)
		self.assertEqual(response.data[0]["event_type"], EventType.WEBINAR)

	def test_online_filter_works_correctly(self):
		response = self.client.get(self.list_url, {"is_online": "true"})
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(len(response.data), 1)
		self.assertTrue(response.data[0]["is_online"])

	def test_rsvp_count_is_returned(self):
		RSVP.objects.create(event=self.future_event, user=self.owner)
		response = self.client.get(self.detail_url)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data["rsvp_count"], 1)


class RSVPViewTests(APITransactionTestCase):
	def setUp(self):
		self.user = User.objects.create_user(
			email="user@example.com", password="testpass123"
		)
		self.other_user = User.objects.create_user(
			email="otheruser@example.com", password="testpass123"
		)
		self.owner = User.objects.create_user(
			email="owner2@example.com", password="testpass123"
		)
		self.event = Event.objects.create(
			title="RSVP Event",
			description="RSVP description",
			date=timezone.now() + timedelta(days=1),
			event_type=EventType.MEETUP,
			created_by=self.owner,
		)
		self.rsvp_url = reverse("event-rsvp", kwargs={"pk": self.event.id})
		self.detail_url = reverse("event-detail", kwargs={"pk": self.event.id})

	def test_authenticated_user_can_rsvp_to_event(self):
		self.client.force_authenticate(user=self.user)
		response = self.client.post(self.rsvp_url)
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertTrue(RSVP.objects.filter(event=self.event, user=self.user).exists())

	def test_unauthenticated_user_cannot_rsvp(self):
		response = self.client.post(self.rsvp_url)
		self.assertIn(
			response.status_code,
			[status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN],
		)

	def test_user_cannot_rsvp_to_same_event_twice(self):
		RSVP.objects.create(event=self.event, user=self.user)
		self.client.force_authenticate(user=self.user)
		response = self.client.post(self.rsvp_url)
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertIn("already RSVPd", str(response.data))

	def test_user_can_cancel_their_rsvp(self):
		RSVP.objects.create(event=self.event, user=self.user)
		self.client.force_authenticate(user=self.user)
		response = self.client.delete(self.rsvp_url)
		self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
		self.assertFalse(RSVP.objects.filter(event=self.event, user=self.user).exists())

	def test_user_cannot_cancel_another_users_rsvp(self):
		RSVP.objects.create(event=self.event, user=self.user)
		self.client.force_authenticate(user=self.other_user)
		response = self.client.delete(self.rsvp_url)
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

	def test_rsvp_count_increases_when_user_rsvps(self):
		self.client.force_authenticate(user=self.user)
		self.client.post(self.rsvp_url)
		response = self.client.get(self.detail_url)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data["rsvp_count"], 1)

	def test_rsvp_count_decreases_when_user_cancels(self):
		RSVP.objects.create(event=self.event, user=self.user)
		self.client.force_authenticate(user=self.user)
		self.client.delete(self.rsvp_url)
		response = self.client.get(self.detail_url)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data["rsvp_count"], 0)
