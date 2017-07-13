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
            file_content = "data:image/gif;base64,\
                            R0lGODlhEAAQAMQAAORHHOVSKudfOulrSOp3WOyDZu6QdvCchPGolfO0o/XBs/\
                            fNwfjZ0frl3/zy7////wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\
                            AAAAAAAAAAAAAAAAAAAACH5BAkAABAALAAAAAAQABAAAAVVICSOZGlCQAosJ6mu7f\
                            iyZeKqNKToQGDsM8hBADgUXoGAiqhSvp5QAnQKGIgUhwFUYLCVDFCrKUE1lBavAViFIDl\
                            TImbKC5Gm2hB0SlBCBMQiB0UjIQA7"
            uploaded_img = uploaded_image(file_content=file_content)
            file_path = uploaded_img.file_path
            actual_file_path = app.config.get('BASE_DIR') + '/static/uploads/' + uploaded_img.filename
            self.assertEqual(file_path, actual_file_path)
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

    def test_upload_multiple_file(self):
        class FileObj(StringIO):

            def close(self):
                pass

        class MyRequest(Request):
            def _get_file_stream(*args, **kwargs):
                return FileObj()

        app.request_class = MyRequest

        @app.route("/test_upload_multi", methods=['POST'])
        def upload_multi():
            files = request.files.getlist('files[]')
            file_uploaded = uploaded_file(files=files, multiple=True)
            files_uploaded = []
            for file in file_uploaded:
                files_uploaded.append({'path': file.file_path,
                                      'name': file.filename})
            return jsonify({"files":files_uploaded})

        with app.test_request_context():
            client = app.test_client()
            resp = client.post('/test_upload_multi',
                               data = {'files[]': [(StringIO('1,2,3,4'), 'test_file.csv'),
                                                   (StringIO('10,20,30,40'), 'test_file2.csv')]})
            datas = json.loads(resp.data)['files']
            for data in datas:
                file_path = data['path']
                filename = data['name']
                actual_file_path = app.config.get('BASE_DIR') + '/static/uploads/' + filename
                self.assertEqual(file_path, actual_file_path)
                self.assertTrue(os.path.exists(file_path))


if __name__ == '__main__':
    unittest.main()
