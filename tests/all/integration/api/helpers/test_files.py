import os
import unittest
from io import BytesIO
from urllib.parse import urlparse

from flask import Request, jsonify, request
from PIL import Image

from app.api.helpers.files import (
    create_save_image_sizes,
    create_save_resized_image,
    uploaded_file,
    uploaded_image,
)
from app.api.helpers.utilities import image_link
from tests.all.integration.utils import OpenEventTestCase


class TestFilesHelperValidation(OpenEventTestCase):
    def getsizes(self, file):
        # get file size *and* image size (None if not known)
        im = Image.open(file)
        return im.size

    def test_uploaded_image_local(self):
        """Method to test uploading image locally"""

        with self.app.test_request_context():
            file_content = "data:image/gif;base64,\
                            R0lGODlhEAAQAMQAAORHHOVSKudfOulrSOp3WOyDZu6QdvCchPGolfO0o/XBs/\
                            fNwfjZ0frl3/zy7////wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\
                            AAAAAAAAAAAAAAAAAAAACH5BAkAABAALAAAAAAQABAAAAVVICSOZGlCQAosJ6mu7f\
                            iyZeKqNKToQGDsM8hBADgUXoGAiqhSvp5QAnQKGIgUhwFUYLCVDFCrKUE1lBavAViFIDl\
                            TImbKC5Gm2hB0SlBCBMQiB0UjIQA7"
            uploaded_img = uploaded_image(file_content=file_content)
            file_path = uploaded_img.file_path
            actual_file_path = (
                self.app.config.get('BASE_DIR')
                + '/static/uploads/'
                + uploaded_img.filename
            )
            assert file_path == actual_file_path
            assert os.path.exists(file_path)

    def test_upload_single_file(self):
        """Method to test uploading of single file"""

        class FileObj(BytesIO):
            def close(self):
                pass

        class MyRequest(Request):
            def _get_file_stream(*args, **kwargs):
                return FileObj()

        self.app.request_class = MyRequest

        @self.app.route("/test_upload", methods=['POST'])
        def upload():
            files = request.files['file']
            file_uploaded = uploaded_file(files=files)
            return jsonify(
                {'path': file_uploaded.file_path, 'name': file_uploaded.filename}
            )

        with self.app.test_request_context():
            client = self.app.test_client()
            resp = client.post(
                '/test_upload', data={'file': (BytesIO(b'1,2,3,4'), 'test_file.csv')}
            )
            data = resp.get_json()
            file_path = data['path']
            filename = data['name']
            actual_file_path = (
                self.app.config.get('BASE_DIR') + '/static/uploads/' + filename
            )
            assert file_path == actual_file_path
            assert os.path.exists(file_path)

    def test_upload_multiple_file(self):
        """Method to test uploading of multiple files"""

        class FileObj(BytesIO):
            def close(self):
                pass

        class MyRequest(Request):
            def _get_file_stream(*args, **kwargs):
                return FileObj()

        self.app.request_class = MyRequest

        @self.app.route("/test_upload_multi", methods=['POST'])
        def upload_multi():
            files = request.files.getlist('files[]')
            file_uploaded = uploaded_file(files=files, multiple=True)
            files_uploaded = []
            for file in file_uploaded:
                files_uploaded.append({'path': file.file_path, 'name': file.filename})
            return jsonify({"files": files_uploaded})

        with self.app.test_request_context():
            client = self.app.test_client()
            resp = client.post(
                '/test_upload_multi',
                data={
                    'files[]': [
                        (BytesIO(b'1,2,3,4'), 'test_file.csv'),
                        (BytesIO(b'10,20,30,40'), 'test_file2.csv'),
                    ]
                },
            )
            datas = resp.get_json()['files']
            for data in datas:
                file_path = data['path']
                filename = data['name']
                actual_file_path = (
                    self.app.config.get('BASE_DIR') + '/static/uploads/' + filename
                )
                assert file_path == actual_file_path
                assert os.path.exists(file_path)

    def test_create_save_resized_image(self):
        """Method to test create resized images"""

        with self.app.test_request_context():
            image_url_test = image_link
            width = 500
            height = 200
            aspect_ratio = False
            upload_path = 'test'
            resized_image_url = create_save_resized_image(
                image_url_test, width, aspect_ratio, height, upload_path, ext='png'
            )
            resized_image_path = urlparse(resized_image_url).path
            resized_image_file = self.app.config.get('BASE_DIR') + resized_image_path
            resized_width, resized_height = self.getsizes(resized_image_file)
            assert os.path.exists(resized_image_file)
            assert resized_width == width
            assert resized_height == height

    def test_create_save_image_sizes(self):
        """Method to test create image sizes"""

        with self.app.test_request_context():
            image_url_test = image_link
            image_sizes_type = "event-image"
            width_large = 1300
            width_thumbnail = 500
            width_icon = 75
            image_sizes = create_save_image_sizes(image_url_test, image_sizes_type)
            image_sizes = {
                url_name: urlparse(image_sizes[url_name]).path for url_name in image_sizes
            }  # Now file names don't contain port (this gives relative urls).

            resized_image_url = image_sizes['original_image_url']
            resized_image_url_large = image_sizes['large_image_url']
            resized_image_url_thumbnail = image_sizes['thumbnail_image_url']
            resized_image_url_icon = image_sizes['icon_image_url']

            resized_image_file = self.app.config.get('BASE_DIR') + resized_image_url
            resized_image_file_large = (
                self.app.config.get('BASE_DIR') + resized_image_url_large
            )
            resized_image_file_thumbnail = (
                self.app.config.get('BASE_DIR') + resized_image_url_thumbnail
            )
            resized_image_file_icon = (
                self.app.config.get('BASE_DIR') + resized_image_url_icon
            )

            resized_width_large, _ = self.getsizes(resized_image_file_large)
            resized_width_thumbnail, _ = self.getsizes(resized_image_file_thumbnail)
            resized_width_icon, _ = self.getsizes(resized_image_file_icon)

            assert os.path.exists(resized_image_file)
            assert resized_width_large == width_large
            assert resized_width_thumbnail == width_thumbnail
            assert resized_width_icon == width_icon


if __name__ == '__main__':
    unittest.main()
