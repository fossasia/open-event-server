import unittest
from app.api.helpers.custom_fields import Color, Email, Uri,\
    ImageUri, DateTime, Integer, Float, ChoiceString, Upload
from tests.utils import OpenEventTestCase
from app import current_app as app


class TestCustomFieldsValidation(OpenEventTestCase):
    """
    Test the validation methods of custom fields
    """
    def _test_common(self, field):
        field.required = False
        self.assertTrue(field.validate(None))
        field.required = True
        self.assertFalse(field.validate(None))
        if field.__schema_type__ != 'string':
            self.assertFalse(field.validate(''))

    def test_color_field(self):
        field = Color()
        self._test_common(field)
        self.assertFalse(field.validate('randomnothing'))
        self.assertTrue(field.validate('black'))
        self.assertTrue(field.validate('#44ff3b'))

    def test_email_field(self):
        field = Email()
        self._test_common(field)
        self.assertFalse(field.validate('website.com'))
        self.assertTrue(field.validate('email@gmail.com'))

    def test_uri_field(self):
        field = Uri()
        self._test_common(field)
        self.assertFalse(field.validate('somestring'))
        self.assertFalse(field.validate('website.com'))
        self.assertFalse(field.validate('www.website.com'))
        self.assertFalse(field.validate('http://bazooka'))
        self.assertTrue(field.validate('http://localhost/file'))
        self.assertTrue(field.validate('http://website.com'))
        self.assertTrue(field.validate('ftp://domain.com/blah'))

    def test_image_uri_field(self):
        field = ImageUri()
        self._test_common(field)
        # same as uri field, not many tests needed
        self.assertFalse(field.validate('imgur.com/image.png'))
        self.assertTrue(field.validate('http://imgur.com/image.png'))

    def test_datetime_field(self):
        field = DateTime()
        self._test_common(field)
        self.assertTrue(field.validate('2014-12-31 23:11:44'))
        self.assertTrue(field.validate('2014-12-31T23:11:44'))
        self.assertFalse(field.validate('2014-31-12T23:11:44'))
        self.assertFalse(field.validate('2014-12-32'))
        self.assertFalse(field.validate('2014-06-30 12:00'))

    def test_integer_field(self):
        field = Integer()
        self._test_common(field)
        self.assertTrue(field.validate(0))
        self.assertFalse(field.validate(-2323.23))
        self.assertFalse(field.validate(2323.23))

    def test_float_field(self):
        field = Float()
        self._test_common(field)
        self.assertTrue(field.validate(92))

    def test_choice_string_field(self):
        field = ChoiceString(choice_list=['a', 'b', 'c'])
        self._test_common(field)
        self.assertTrue(field.validate('a'))
        self.assertFalse(field.validate('d'))
        self.assertFalse(field.validate('ab'))

    def test_upload_field(self):
        with app.test_request_context():
            field = Upload()
            self._test_common(field)
            link = '/static/1'
            self.assertTrue(field.validate(link))
            z = field.format(link)
            self.assertNotEqual(link, z)
            self.assertTrue(field.validate(z), msg=z)
            self.assertEqual('http://site.co/1', field.format('http://site.co/1'))


if __name__ == '__main__':
    unittest.main()
