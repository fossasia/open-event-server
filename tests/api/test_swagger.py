import unittest

from tests.utils import OpenEventTestCase


class TestSwagger(OpenEventTestCase):
    """
    Tests Swagger UI and json
    """
    def test_swagger_ui(self):
        resp = self.app.get('/api/v2', follow_redirects=True)
        self.assertIn('Open Event', resp.data)

    def test_swagger_json(self):
        """
        tests swagger.json. Also writes the file
        """
        resp = self.app.get('/api/v2/swagger.json')
        self.assertIn('event', resp.data)
        fp = open('static/temp/swagger.json', 'w')
        fp.write(resp.data)
        fp.close()


if __name__ == '__main__':
    unittest.main()
