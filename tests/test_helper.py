"""Copyright 2015 Rafal Kowalski"""
import unittest
from tests.utils import OpenEventTestCase
from mock import patch

from tests.object_mother import ObjectMother
from tests.setup_database import Setup
from open_event import current_app as app
from open_event.models import db
from open_event.models.version import Version
from open_event.helpers.data import DataManager, update_version, save_to_db


class TestDataManager(OpenEventTestCase):
    def setUp(self):
        self.app = Setup.create_app()
        with app.test_request_context():
            db.session.add(ObjectMother.get_event())
            db.session.commit()


    def _delete_object_from_db(self):
        DataManager().remove_microlocation(1)


    @patch.object(db.session, "rollback")
    def test_rollback_called_when_object_doesnt_exist(self, method):
        with app.test_request_context():
            self._delete_object_from_db()
            self.assertTrue(method.called)

    def test_update_version_function(self):
        with app.test_request_context():
            update_version(1, True, "tracks_ver")
            self.assertEqual(Version.query.get(1).id, 1)
            self.assertEqual(Version.query.get(1).tracks_ver, 0)
            update_version(1, False, "tracks_ver")
            self.assertEqual(Version.query.get(2).tracks_ver, 1)

    def test_increasing_version_after_update_version_called(self):
        with app.test_request_context():
            self.assertEqual(len(Version.query.all()), 0)
            update_version(1, True, "tracks_ver")
            self.assertEqual(len(Version.query.all()), 1)

    @patch.object(db.session, "commit")
    def test_save_to_db_called_db_session_commit(self, method):
        with app.test_request_context():
            self._create_microlocation()
        self.assertTrue(method.called)

    @patch.object(db.session, "rollback")
    def test_save_to_db_called_db_session_rollback(self, method):
        with app.test_request_context():
            try:
                self._create_microlocation()
            except Exception:
                pass
            self.assertTrue(not method.called)


if __name__ == '__main__':
    unittest.main()
