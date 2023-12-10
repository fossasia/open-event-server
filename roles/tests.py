from django.test import TestCase

from .models import Role


class BlogTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.role = Role.objects.create(
            name="dummy_role",
            title_name="Dummy Role",
        )

    def test_role_model(self):
        self.assertEqual(self.role.name, "dummy_role")
        self.assertEqual(str(self.role), "Dummy Role")
