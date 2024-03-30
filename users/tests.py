from django.test import TestCase  # noqa: F401

# Create your tests here.
from .models import Exhibitor, CustomUser  
from .forms import ExhibitorCreationForm, ExhibitorChangeForm

class ExhibitorTestCase(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create(username="test_user")
        self.exhibitor = Exhibitor.objects.create(
            username=self.user,
            description="Test Description",
            website="http://example.com"
        )

    def test_exhibitor_creation(self):
        self.assertEqual(self.exhibitor.username, self.user)
        self.assertEqual(self.exhibitor.description, "Test Description")
        self.assertEqual(self.exhibitor.website, "http://example.com")

class ExhibitorFormTestCase(TestCase):
    def test_valid_creation_form(self):
        form_data = {'username': 'test_user', 'description': 'Test Description', 'website': 'http://example.com'}
        form = ExhibitorCreationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_creation_form(self):
        form_data = {'username': 'test_user', 'description': '', 'website': 'invalid-url'}
        form = ExhibitorCreationForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_valid_change_form(self):
        form_data = {'description': 'New Description', 'website': 'http://new-example.com'}
        form = ExhibitorChangeForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_change_form(self):
        form_data = {'description': '', 'website': 'invalid-url'}
        form = ExhibitorChangeForm(data=form_data)
        self.assertFalse(form.is_valid())