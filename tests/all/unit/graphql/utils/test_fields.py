from unittest import TestCase

from app.api.schema.settings import SettingSchemaPublic
from app.graphql.utils.fields import extract_from_marshmallow


class TestFields(TestCase):
    def test_extracts_fields(self):
        self.assertTrue(
            set(extract_from_marshmallow(SettingSchemaPublic)).issuperset(
                {'id', 'app_name', 'is_paytm_activated'}
            )
        )
        self.assertFalse(
            set(extract_from_marshmallow(SettingSchemaPublic)).issuperset(
                {'paypal_secret'}
            )
        )
