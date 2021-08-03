import unittest

from app.api.helpers.log import record_activity
from app.models import db
from app.models.activity import Activity
from tests.all.integration.auth_helper import create_user
from tests.all.integration.utils import OpenEventTestCase


class TestLogging(OpenEventTestCase):
    def test_record_activity_valid_template(self):
        """Test to record activity for valid template"""
        with self.app.test_request_context():
            test_user = create_user(email="logging@test.com", password="logpass")
            record_activity('create_user', login_user=test_user, user=test_user)
            user_id_format = ' (' + str(test_user.id) + ')'
            test_actor = test_user.email + user_id_format
            assert 'User logging@test.com' + user_id_format + ' created', \
                db.session.query(Activity).filter_by(actor=test_actor).first().action

    def test_record_activity_invalid_template(self):
        """Test to record activity for invalid template"""
        with self.app.test_request_context():
            test_user = create_user(email="logging@test.com", password="logpass")
            record_activity('invalid_template', login_user=test_user, user=test_user)
            user_id_format = ' (' + str(test_user.id) + ')'
            test_actor = test_user.email + user_id_format
            assert '[ERROR LOGGING] invalid_template', \
                db.session.query(Activity).filter_by(actor=test_actor).first().action


if __name__ == '__main__':
    unittest.main()
