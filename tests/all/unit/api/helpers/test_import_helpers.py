import unittest
from unittest.mock import patch

from app.api.helpers.errors import ServerError
from app.api.helpers.import_helpers import (
    _allowed_file,
    _available_path,
    _trim_id,
    make_error,
)


class TestImportHelpers(unittest.TestCase):
    def test_allowed_file(self):
        """Method to test a valid file name"""

        # Test a valid filename
        request_filename = 'test.pdf'
        request_extensions = ['pdf', 'zip']
        actual_response = _allowed_file(request_filename, request_extensions)
        self.assertTrue(actual_response)

        # Test an invalid filename
        request_filename = 'test.pdf'
        request_extensions = ['zip']
        actual_response = _allowed_file(request_filename, request_extensions)
        self.assertFalse(actual_response)

    def test_available_path(self):
        """Method to test available path"""

        # Test when the path is available
        with patch('app.api.helpers.import_helpers.os.path.isfile', return_value=False):
            expected_response = 'testfile.pdf'
            actual_response = _available_path('test', 'file.pdf')
            self.assertEqual(expected_response, actual_response)

        # Test when the entered path already exists
        with patch(
            'app.api.helpers.import_helpers.os.path.isfile',
            side_effect=[True, True, False],
        ):
            expected_response = 'testfilename2'
            actual_response = _available_path('test', 'filename')
            self.assertEqual(expected_response, actual_response)

    def test_make_error(self):
        """Method to test make_error function"""

        # When er is None and _id is None
        expected_response_title = 'File event, Internal Server Error'
        expected_response_status = 500
        actual_response = make_error('event')
        self.assertEqual(expected_response_status, actual_response.status)
        self.assertEqual(expected_response_title, actual_response.title)
        self.assertIsInstance(actual_response, ServerError)

        # When er is not None, _id is None, er doesen't have title and status
        error = ServerError(source='Zip Upload', detail='Invalid json')
        expected_response_title = 'File event, Internal Server Error'
        expected_response_status = 500
        actual_response = make_error('event', er=error)
        self.assertEqual(expected_response_status, actual_response.status)
        self.assertEqual(expected_response_title, actual_response.title)
        self.assertIsInstance(actual_response, ServerError)

        # When er is not None, _id is None, er have title but not status
        error = ServerError(
            source='Zip Upload', detail='Invalid json', title="Error while uploading."
        )
        expected_response_title = 'File event, Error while uploading.'
        expected_response_status = 500
        actual_response = make_error('event', er=error)
        self.assertEqual(expected_response_status, actual_response.status)
        self.assertEqual(expected_response_title, actual_response.title)
        self.assertIsInstance(actual_response, ServerError)

        # When er is not None, _id is None, er doesn't have title but has status
        error = ServerError(source='Zip Upload', detail='Invalid json', status=404)
        expected_response_title = 'File event, Internal Server Error'
        expected_response_status = 404
        actual_response = make_error('event', er=error)
        self.assertEqual(expected_response_status, actual_response.status)
        self.assertEqual(expected_response_title, actual_response.title)
        self.assertIsInstance(actual_response, ServerError)

        # When er is not None, _id is None, er have title and status
        error = ServerError(
            source='Zip Upload',
            detail='Invalid json',
            title="Error while uploading.",
            status=403,
        )
        expected_response_title = 'File event, Error while uploading.'
        expected_response_status = 403
        actual_response = make_error('event', er=error)
        self.assertEqual(expected_response_status, actual_response.status)
        self.assertEqual(expected_response_title, actual_response.title)
        self.assertIsInstance(actual_response, ServerError)

        # When er and _id are not None
        error = ServerError(
            source='{}', detail='Internal Server Error', title='Internal Server Error'
        )
        expected_response_title = 'File event, ID ERR_255, Internal Server Error'
        expected_response_status = 500
        actual_response = make_error('event', er=error, id_='ERR_255')
        self.assertEqual(expected_response_status, actual_response.status)
        self.assertEqual(expected_response_title, actual_response.title)
        self.assertIsInstance(actual_response, ServerError)

        # When er is None and _id is not None
        actual_response = make_error('event', id_='ERR_255')
        expected_response_title = 'File event, ID ERR_255, Internal Server Error'
        expected_response_status = 500
        self.assertEqual(expected_response_status, actual_response.status)
        self.assertEqual(expected_response_title, actual_response.title)
        self.assertIsInstance(actual_response, ServerError)

    def test_trim_id(self):
        """Method to test trim_id"""

        data = {'id': 'e34234'}
        expected_response = ('e34234', {})
        actual_response = _trim_id(data)
        self.assertEqual(expected_response, actual_response)

        data = {'id': 'e34234', 'details': 'This is a test event', 'Venue': 'Fossasia'}
        expected_response = (
            'e34234',
            {'details': 'This is a test event', 'Venue': 'Fossasia'},
        )
        actual_response = _trim_id(data)
        self.assertEqual(expected_response, actual_response)
