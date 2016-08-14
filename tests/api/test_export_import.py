import unittest
import json
import logging
import shutil
import zipfile
import time
import os
from StringIO import StringIO

from tests.setup_database import Setup
from tests.utils import OpenEventTestCase
from tests.api.utils import create_event, get_path, create_services,\
    create_session, save_to_db, Speaker
from tests.auth_helper import register
from app import current_app as app


class ImportExportBase(OpenEventTestCase):
    """
    Helper functions to test import/export
    """
    def _upload(self, data, url, filename='anything'):
        return self.app.post(
            url,
            data={'file': (StringIO(data), filename)}
        )

    def _put(self, path, data):
        return self.app.put(
            path,
            data=json.dumps(data),
            headers={'content-type': 'application/json'}
        )

    def _post(self, path, data):
        return self.app.post(
            path,
            data=json.dumps(data),
            headers={'content-type': 'application/json'}
        )

    def _do_successful_export(self, event_id, config={'image': True}):
        path = get_path(event_id, 'export', 'json')
        resp = self._post(path, config)
        self.assertEqual(resp.status_code, 200)
        # watch task
        self.assertIn('task_url', resp.data)
        task_url = json.loads(resp.data)['task_url']
        # wait for done
        while True:
            resp = self.app.get(task_url)
            if 'SUCCESS' in resp.data:
                self.assertIn('download_url', resp.data)
                dl = json.loads(resp.data)['result']['download_url']
                break
            time.sleep(1)
        # get event
        resp = self.app.get(dl)
        self.assertEqual(resp.status_code, 200)
        return resp

    def _create_set(self, event_id=1, config={'image': True}):
        """
        exports and extracts in static/temp/test_event_import
        """
        # export
        resp = self._do_successful_export(event_id, config)
        zip_file = StringIO()
        zip_file.write(resp.data)
        # extract
        path = 'static/temp/test_event_import'
        if os.path.isdir(path):
            shutil.rmtree(path, ignore_errors=True)
        with zipfile.ZipFile(zip_file) as z:
            z.extractall(path)


class TestEventExport(ImportExportBase):
    """
    Test export of event
    """
    def setUp(self):
        self.app = Setup.create_app()
        with app.test_request_context():
            register(self.app, u'test@example.com', u'test')
            create_event(creator_email=u'test@example.com')
            create_services(1)

    def test_export_success(self):
        resp = self._do_successful_export(1)
        self.assertIn('event1.zip', resp.headers['Content-Disposition'])
        size = len(resp.data)
        with app.test_request_context():
            create_services(1, '2')
            create_services(1, '3')
        # check if size increased
        resp = self._do_successful_export(1)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(len(resp.data) > size)

    def test_export_no_event(self):
        path = get_path(2, 'export', 'json')
        resp = self._post(path, {})
        if resp.status_code == 404:  # when celery not running
            return
        task_url = json.loads(resp.data)['task_url']
        resp = self.app.get(task_url)
        self.assertEqual(resp.status_code, 404)

    def test_export_media(self):
        """
        test successful export of media (and more)
        """
        resp = self._put(get_path(1), {'logo': 'https://placehold.it/350x150'})
        self.assertIn('placehold', resp.data, resp.data)
        self._create_set()
        dr = 'static/temp/test_event_import'
        data = open(dr + '/event', 'r').read()
        self.assertIn('images/logo', data)
        self.assertEqual(json.loads(data)['creator'].get('id'), None)  # test no ID of creator
        obj = json.loads(data)
        logo_data = open(dr + obj['logo'], 'r').read()
        self.assertTrue(len(logo_data) > 10)
        # test meta.json
        data = open(dr + '/meta', 'r').read()
        self.assertIn('http', data)

    def test_export_settings_marshal(self):
        """
        test if export settings are marshalled by default properly
        Also check when settings are all False, nothing is exported
        """
        resp = self._put(get_path(1), {'logo': 'https://placehold.it/350x150'})
        self.assertIn('placehold', resp.data, resp.data)
        self._create_set(1, {})
        dr = 'static/temp/test_event_import'
        data = open(dr + '/event', 'r').read()
        obj = json.loads(data)
        self.assertIn('placehold', obj['logo'])
        if os.path.isdir(dr + '/images'):
            self.assertFalse(1, 'Image Dir Exists')

    def test_export_order(self):
        """
        Tests order of export of fields in export files
        """
        self._create_set()
        dr = 'static/temp/test_event_import'
        # event
        data = open(dr + '/event', 'r').read()
        self.assertTrue(data.find('id') < data.find('background_image'))
        self.assertTrue(data.find('location_name') < data.find('copyright'))
        # sessions (a service)
        data = open(dr + '/sessions', 'r').read()
        self.assertTrue(data.find('id') < data.find('audio'))
        self.assertTrue(data.find('short_abstract') < data.find('slides'))
        # sponsors (a service)
        data = open(dr + '/sponsors', 'r').read()
        self.assertTrue(data.find('name') < data.find('description'))


class TestEventImport(ImportExportBase):
    """
    Test import of event
    """
    def setUp(self):
        self.app = Setup.create_app()
        with app.test_request_context():
            register(self.app, u'test@example.com', u'test')
            create_event(creator_email='test@example.com')
            create_services(1, '1')
            create_services(1, '2')
            create_services(1, '3')

    def _test_import_success(self):
        # first export
        resp = self._do_successful_export(1)
        file = resp.data
        # import
        upload_path = get_path('import', 'json')
        resp = self._upload(file, upload_path, 'event.zip')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('task_url', resp.data)
        task_url = json.loads(resp.data)['task_url']
        # wait for done
        while True:
            resp = self.app.get(task_url)
            if 'SUCCESS' in resp.data:
                self.assertIn('result', resp.data)
                dic = json.loads(resp.data)['result']
                break
            if resp.status_code != 200:
                self.assertTrue(False, 'FAIL')
            logging.info(resp.data)
            time.sleep(2)
        # check internals
        self.assertEqual(dic['id'], 2)
        self.assertEqual(dic['name'], 'TestEvent')
        self.assertIn('fb.com', json.dumps(dic['social_links']), dic)
        # get to check final
        resp = self.app.get(get_path(2))
        self.assertEqual(resp.status_code, 200)
        self.assertIn('TestEvent', resp.data)
        # No errors generally means everything went fine
        # The method will crash and return 500 in case of any problem

    def _test_import_error(self, checks=[]):
        # first export
        resp = self._do_successful_export(1)
        file = resp.data
        # import
        upload_path = get_path('import', 'json')
        resp = self._upload(file, upload_path, 'event.zip')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('task_url', resp.data)
        task_url = json.loads(resp.data)['task_url']
        # wait for done
        while True:
            resp = self.app.get(task_url)
            if resp.status_code != 200:
                break
            logging.info(resp.data)
            time.sleep(2)
        # checks
        for i in checks:
            self.assertIn(i, resp.data, resp.data)

    def test_import_simple(self):
        self._test_import_success()

    def test_import_extended(self):
        with app.test_request_context():
            create_session(
                1, '4', track=1, session_type=1,
                microlocation=1, speakers=[2, 3])
            create_session(
                1, '5', track=2, speakers=[1]
            )
        self._test_import_success()

    def test_import_validation_error(self):
        """
        tests if error is returned correctly.
        Needed after task was run through celery
        """
        with app.test_request_context():
            speaker = Speaker(
                name='SP',
                email='invalid_email',
                organisation='org',
                country='japan',
                event_id=1)
            save_to_db(speaker, 'speaker invalid saved')
        self._test_import_error(
            checks=['Invalid', 'email', '400']
        )


class TestImportOTS(ImportExportBase):
    """
    Tests import of OTS sample
    """
    def setUp(self):
        self.app = Setup.create_app()
        with app.test_request_context():
            register(self.app, u'test@example.com', u'test')

    def _test_import_ots(self):
        dir_path = 'samples/ots16'
        shutil.make_archive(dir_path, 'zip', dir_path)
        file = open(dir_path + '.zip', 'r').read()
        os.remove(dir_path + '.zip')
        upload_path = get_path('import', 'json')
        resp = self._upload(file, upload_path, 'event.zip')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('Open Tech Summit', resp.data)


if __name__ == '__main__':
    unittest.main()
