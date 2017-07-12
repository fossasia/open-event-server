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

  
if __name__ == '__main__':
    unittest.main()
