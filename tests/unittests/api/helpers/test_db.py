import unittest

from app import current_app as app
from tests.unittests.utils import OpenEventTestCase
from app.factories.event import EventFactoryBasic
from app.api.helpers.db import save_to_db, safe_query
from flask_rest_jsonapi.exceptions import ObjectNotFound
from app.models import db
from app.models.event import Event
from tests.unittests.setup_database import Setup


class TestDBHelperValidation(OpenEventTestCase):
    def setUp(self):
        self.app = Setup.create_app()

    def test_save_to_db(self):
        with app.test_request_context():
            obj = EventFactoryBasic()
            save_to_db(obj)
            event = db.session.query(Event).filter(Event.id == obj.id).first()
            self.assertEqual(obj.name, event.name)

    def test_safe_query(self):
        with app.test_request_context():
            event = EventFactoryBasic()
            db.session.add(event)
            db.session.commit()
            obj = safe_query(db, Event, 'id', event.id, 'event_id')
            self.assertEqual(obj.name, event.name)

    def test_safe_query_exception(self):
        with app.test_request_context():
            self.assertRaises(ObjectNotFound, lambda: safe_query(db, Event, 'id', 1, 'event_id'))


if __name__ == '__main__':
    unittest.main()
