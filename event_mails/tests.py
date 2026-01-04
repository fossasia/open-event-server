# Create your tests here.
from rest_framework.test import APITestCase
from rest_framework import status

from .models import EventMail


class EventMailAPITest(APITestCase):

    def test_create_event_mail(self):
        data = {
            "event_id": 1,
            "email": "test@example.com",
            "role": "organizer"
        }

        response = self.client.post("/v2/event-mails/", data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(EventMail.objects.count(), 1)
        self.assertEqual(EventMail.objects.first().email, "test@example.com")

    def test_missing_fields(self):
        response = self.client.post("/v2/event-mails/", {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_event_mails(self):
        EventMail.objects.create(event_id=1, email="a@test.com", role="organizer")

        response = self.client.get("/v2/event-mails/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_retrieve_update_delete(self):
        mail = EventMail.objects.create(event_id=1, email="a@test.com", role="organizer")

        # Retrieve
        response = self.client.get(f"/v2/event-mails/{mail.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Update
        response = self.client.patch(f"/v2/event-mails/{mail.id}/", {"role": "speaker"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(EventMail.objects.get(id=mail.id).role, "speaker")

        # Delete
        response = self.client.delete(f"/v2/event-mails/{mail.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(EventMail.objects.count(), 0)
