from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import EventMail

User = get_user_model()


class EventMailAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="password123"
        )

        response = self.client.post(
            "/api/token/",
            {"username": "testuser", "password": "password123"},
            format="json"
        )

        self.token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + self.token)

    def test_create_event_mail(self):
        payload = {
            "event_id": 1,
            "subject": "Test Subject",
            "body": "Test Body",
            "recipients": "all"
        }

        response = self.client.post("/v2/event-mails/", payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(EventMail.objects.count(), 1)
        self.assertEqual(EventMail.objects.first().subject, "Test Subject")

    def test_list_event_mails(self):
        EventMail.objects.all().delete()

        EventMail.objects.create(
            event_id=1,
            subject="A",
            body="B",
            recipients="all",
            created_by=self.user.id
        )

        response = self.client.get("/v2/event-mails/?event_id=1")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data),1)
