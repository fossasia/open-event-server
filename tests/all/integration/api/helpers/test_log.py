from tests.all.integration.setup_database import Setup
from app import current_app as app
from tests.all.integration.utils import OpenEventTestCase
from app.api.helpers.log import record_activity
from app.models.activity import Activity, ACTIVITIES
from tests.all.integration.auth_helper import create_user
from app.models import db

import unittest


class TestLogging(OpenEventTestCase):
    def setUp(self):
        self.app = Setup.create_app()
    
    def test_record_activity_valid_template(self):
        test_user = create_user(email="logging@test.com", password="logpass")
        record_activity('create_user', login_user=test_user, user=test_user)
        test_actor = test_user.email + ' (' + str(test_user.id) + ')'
        self.assertTrue(db.session.query(Activity).filter_by(actor=test_actor).first().msg,
                        'User logging@test.com' + ' (' +test_user.id+')'+' created')
    
    def test_record_activity_invalid_template(self):
        test_user = create_user(email="logging@test.com", password="logpass")
        record_activity('invalid_template', login_user=test_user, user=test_user)
        test_actor = test_user.email + ' (' + str(test_user.id) + ')'
        self.assertTrue(db.session.query(Activity).filter_by(actor=test_actor).first().msg, '[ERROR LOGGING] invalid_template')


if __name__ == '__main__':
    unittest.main()


        

