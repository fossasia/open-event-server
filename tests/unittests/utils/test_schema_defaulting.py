import unittest

from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Schema

from app import current_app as app
from app.api.helpers.utilities import dasherize
from utils.common import patch_defaults


class TestSchema(Schema):
    """
    Api schema for Testing Purposes
    """

    class Meta:
        """
        Meta class for the test Schema
        """
        type_ = 'test-schema'
        inflect = dasherize

    id = fields.Str(dump_only=True)
    field_without_default = fields.Str(required=True)
    field_with_default = fields.Boolean(required=True, default=False)


class TestUtils:

    def test_patch_defaults_adds_defaults(self):
        with app.test_request_context():
            schema = TestSchema()
            data = {
                'field_without_default': 'value_field_without_default'
            }
            patched_data = patch_defaults(schema, data)
            self.assertEqual(patched_data.get('field_with_default'), False)

    def test_patch_defaults_leaves_other_fields_untouched(self):
        with app.test_request_context():
            schema = TestSchema()
            data = {
                'field_without_default': 'value_field_without_default'
            }
            patched_data = patch_defaults(schema, data)
            self.assertEqual(patched_data.get('field_without_default'), 'value_field_without_default')


if __name__ == '__main__':
    unittest.main()
