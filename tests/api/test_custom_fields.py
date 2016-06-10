import unittest
from open_event.api.custom_fields import ColorField, EmailField, UriField,\
    ImageUriField


class TestCustomFieldsValidation(unittest.TestCase):
    """
    Test the validation methods of custom fields
    """
    def _test_empty_field(self, field):
        field.required = False
        self.assertTrue(field.validate(''))
        self.assertTrue(field.validate(None))
        field.required = True
        self.assertFalse(field.validate(None))
        self.assertFalse(field.validate(''))

    def test_color_field(self):
        field = ColorField()
        self._test_empty_field(field)
        self.assertFalse(field.validate('randomnothing'))
        self.assertTrue(field.validate('black'))
        self.assertTrue(field.validate('#44ff3b'))

    def test_email_field(self):
        field = EmailField()
        self._test_empty_field(field)
        self.assertFalse(field.validate('website.com'))
        self.assertTrue(field.validate('email@gmail.com'))

    def test_uri_field(self):
        field = UriField()
        self._test_empty_field(field)
        self.assertFalse(field.validate('somestring'))
        self.assertFalse(field.validate('website.com'))
        self.assertFalse(field.validate('www.website.com'))
        self.assertTrue(field.validate('http://website.com'))
        self.assertTrue(field.validate('ftp://domain.com/blah'))

    def test_image_uri_field(self):
        field = ImageUriField()
        self._test_empty_field(field)
        # same as uri field, not many tests needed
        self.assertFalse(field.validate('imgur.com/image.png'))
        self.assertTrue(field.validate('http://imgur.com/image.png'))


if __name__ == '__main__':
    unittest.main()
