import unittest
from unittest.mock import patch

from app.api.helpers.files import make_frontend_url


class TestFilesMethods(unittest.TestCase):

    def test_frontend_url(self):
        """Test whether frontend_url is created correctly"""

        def patch_settings(settings, url):
            settings.return_value = {
                'frontend_url': url
            }

        with patch('app.api.helpers.files.get_settings') as get_settings:
            get_settings.return_value = {}
            self.assertEqual('verify?token=hi',
                             make_frontend_url('/verify', {'token': 'hi'}))

            patch_settings(get_settings, 'https://next.eventyay.com/')
            self.assertEqual('https://next.eventyay.com/verify?token=ok_this_is_a_secret',
                             make_frontend_url('/verify', {'token': 'ok_this_is_a_secret'}))

            self.assertEqual('https://next.eventyay.com/verify?token=ok_this_is_a_secret',
                             make_frontend_url('/verify', {'token': 'ok_this_is_a_secret'}))

            self.assertEqual('https://next.eventyay.com/verify',
                             make_frontend_url('/verify'))

            patch_settings(get_settings, 'https://next.eventyay.com')
            self.assertEqual('https://next.eventyay.com/verify?token=ok_this_is_a_secret',
                             make_frontend_url('verify', {'token': 'ok_this_is_a_secret'}))

            patch_settings(get_settings, 'https://fossasia.github.io/open-event-frontend/')
            self.assertEqual('https://fossasia.github.io/open-event-frontend/verify?token=ok_this_is_a_secret',
                             make_frontend_url('/verify', {'token': 'ok_this_is_a_secret'}))

            patch_settings(get_settings, 'https://fossasia.github.io/open-event-frontend')
            self.assertEqual('https://fossasia.github.io/open-event-frontend/verify?token=ok_this_is_a_secret',
                             make_frontend_url('/verify', {'token': 'ok_this_is_a_secret'}))


if __name__ == '__main__':
    unittest.main()
