import unittest
import json
import zipfile
import shutil
import time
import os
from StringIO import StringIO

from tests.setup_database import Setup
from tests.api.utils import create_event, get_path, create_services
from tests.auth_helper import register
from open_event import current_app as app
from test_export_import import ImportExportBase


class TestImportUploads(ImportExportBase):
    """
    Test Import for media uploads
    """
    def setUp(self):
        self.app = Setup.create_app()
        with app.test_request_context():
            register(self.app, u'test@example.com', u'test')
            create_event(creator_email='test@example.com')
            create_services(1, '1')

    def _create_set(self):
        # export
        resp = self._do_successful_export(1)
        zip_file = StringIO()
        zip_file.write(resp.data)
        # extract
        path = 'static/temp/test_event_import'
        if os.path.isdir(path):
            shutil.rmtree(path, ignore_errors=True)
        with zipfile.ZipFile(zip_file) as z:
            z.extractall(path)

    def _update_json(self, file, field, value, number=None):
        fp = 'static/temp/test_event_import/%s.json' % file
        ptr = open(fp)
        data = json.loads(ptr.read())
        if file == 'event':
            data[field] = value
        else:
            data[number - 1][field] = value
        ptr.close()
        ptr = open(fp, 'w')
        ptr.write(json.dumps(data, indent=4))
        ptr.close()

    def _create_file(self, name):
        f = open('static/temp/test_event_import/%s' % name, 'w+')
        f.write('test')
        f.close()

    def _get_event_value(self, path, field):
        resp = self.app.get(path)
        self.assertEqual(resp.status_code, 200, resp.data)
        data = json.loads(resp.data)
        return data[field]

    def _make_zip_from_dir(self):
        dir_path = 'static/temp/test_event_import'
        shutil.make_archive(dir_path, 'zip', dir_path)
        file = open(dir_path + '.zip', 'r').read()
        os.remove(dir_path + '.zip')
        return file

    def _do_succesful_import(self, file):
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
            time.sleep(2)
        return dic

    def test_media_successful_uploads(self):
        """
        Test successful uploads of relative and direct links,
        both types of media
        """
        self._create_set()
        self._update_json('event', 'background_url', '/bg.png')
        self._create_file('bg.png')
        self._update_json('speakers', 'photo', '/spkr.png', 1)
        self._create_file('spkr.png')
        self._update_json('sponsors', 'logo', 'http://google.com/favicon.ico', 1)
        # import
        data = self._make_zip_from_dir()
        event_dic = self._do_succesful_import(data)
        # checks
        resp = self.app.get(event_dic['background_url'])
        self.assertEqual(resp.status_code, 200)
        # speaker
        photo = self._get_event_value(
            get_path(2, 'speakers', 2), 'photo'
        )
        resp = self.app.get(photo)
        self.assertEqual(resp.status_code, 200)
        self.assertIn('http://', photo)
        # sponsor
        logo = self._get_event_value(
            get_path(2, 'sponsors', 2), 'logo'
        )
        self.assertIn('sponsors', logo)
        self.assertNotEqual(logo, 'http://google.com/favicon.ico')
        resp = self.app.get(logo)
        self.assertEqual(resp.status_code, 200)

    def test_non_existant_media_import(self):
        """
        Tests when relative link to a media if non-existant
        """
        self._create_set()
        self._update_json('event', 'background_url', '/non.png')
        # import
        data = self._make_zip_from_dir()
        event_dic = self._do_succesful_import(data)
        # check
        self.assertEqual(event_dic['background_url'], None)


if __name__ == '__main__':
    unittest.main()
