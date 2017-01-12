import json
import unittest

from tests.unittests.utils import OpenEventTestCase


class TestSwagger(OpenEventTestCase):
    """
    Tests Swagger things
    """

    def test_swagger_ui(self):
        resp = self.app.get('/api/v1', follow_redirects=True)
        self.assertIn('API', resp.data)

    def test_swagger_json(self):
        """
        tests swagger.json. Also writes the file so that auto-build
        of gh-pages can run
        """
        resp = self.app.get('/api/v1/swagger.json')
        self.assertIn('event', resp.data)
        data = json.loads(resp.data)
        fp = open('static/uploads/swagger.json', 'w')
        fp.write(json.dumps(data, indent=2, sort_keys=True))
        fp.close()


if __name__ == '__main__':
    unittest.main()
