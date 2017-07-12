import unittest
import os
import json

from flask import Request, request, jsonify
from StringIO import StringIO
from app import current_app as app
from tests.unittests.utils import OpenEventTestCase
from app.api.helpers.files import uploaded_image, uploaded_file 
from app.api.helpers.files import create_save_resized_image, create_save_image_sizes
from tests.unittests.setup_database import Setup


class TestFilesHelperValidation(OpenEventTestCase):
    def setUp(self):
        self.app = Setup.create_app()

    def test_uploaded_image_local(self):
        with app.test_request_context():
            file_content = "R0lGODlhEAAQAMQAAORHHOVSKudfOulrSOp3WOyDZu6QdvCchPGol\
            			   fO0o/XBs/fNwfjZ0frl3/zy7////wAAAAAAAAAAAAAAAAAAAAAAAAA\
            			   AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACH5BAkAABAALAAAAAA\
            			   QABAAAAVVICSOZGlCQAosJ6mu7fiyZeKqNKToQGDsM8hBADgUXoGAiqh\
            			   Svp5QAnQKGIgUhwFUYLCVDFCrKUE1lBavAViFIDlTImbKC5Gm2hB0SlB\
            			   CBMQiB0UjIQA7"
            uploaded_img = uploaded_image(file_content=file_content)
            file_path = uploaded_img.file_path
            actual_file_path = app.config.get('BASE_DIR') + '/static/uploads/' + uploaded_img.filename
            self.assertEqual(1, 2)
            self.assertTrue(os.path.exists(file_path))

    def test_upload_single_file(self):

        class FileObj(StringIO):

            def close(self):
                pass

        class MyRequest(Request):
            def _get_file_stream(*args, **kwargs):
                return FileObj()

        app.request_class = MyRequest

        @app.route("/test_upload", methods=['POST'])
        def upload():
            files = request.files['file']
            file_uploaded = uploaded_file(files=files)
            return jsonify(
                {'path': file_uploaded.file_path,
                 'name': file_uploaded.filename})

        with app.test_request_context():
            client = app.test_client()
            resp = client.post('/test_upload', data = {'file': (StringIO('1,2,3,4'), 'test_file.csv')})
            data = json.loads(resp.data)
            file_path = data['path']
            filename = data['name']
            actual_file_path = app.config.get('BASE_DIR') + '/static/uploads/' + filename
            self.assertEqual(file_path, actual_file_path)
            self.assertTrue(os.path.exists(file_path))

if __name__ == '__main__':
    unittest.main()
