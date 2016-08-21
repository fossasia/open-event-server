import unittest
import time

from flask import url_for
from werkzeug.contrib.profiler import ProfilerMiddleware

from tests.unittests.views.view_test_case import OpenEventTestCase
from app.models import db
from app import current_app as app
from populate_db import populate
from tests.unittests.object_mother import ObjectMother
from flask.ext.sqlalchemy import get_debug_queries
from config import ProductionConfig
from tests.unittests.setup_database import Setup

class TestEvents(OpenEventTestCase):
    def setUp(self):
        self.app = Setup.create_app()
        app.config['TESTING'] = True
        app.secret_key = 'super secret key'
        app.config['PROFILE'] = True
        app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[30])
        with app.test_request_context():
            db.create_all()
            populate()

    def test_db_events(self):
        with app.test_request_context():
            start = time.clock()
            for i in range(1, 10000):
                event = ObjectMother.get_event()
                event.name = 'Event' + str(i)
                db.session.add(event)
            db.session.commit()
            url = url_for('sadmin_events.index_view')
            self.app.get(url, follow_redirects=True)
            print time.clock() - start
            for query in get_debug_queries():
                if query.duration >= ProductionConfig.DATABASE_QUERY_TIMEOUT:
                    app.logger.warning("SLOW QUERY: %s\nParameters: %s\nDuration: %fs\nContext: %s\n" % (
                        query.statement, query.parameters, query.duration, query.context))

    def test_db_sessions(self):
        with app.test_request_context():
            start = time.clock()
            for i in range(1, 10000):
                session = ObjectMother.get_session()
                session.name = 'Session' + str(i)
                db.session.add(session)
            db.session.commit()
            url = url_for('sadmin_sessions.display_my_sessions_view')
            self.app.get(url, follow_redirects=True)
            print time.clock() - start
            for query in get_debug_queries():
                if query.duration >= ProductionConfig.DATABASE_QUERY_TIMEOUT:
                    app.logger.warning("SLOW QUERY: %s\nParameters: %s\nDuration: %fs\nContext: %s\n" % (
                        query.statement, query.parameters, query.duration, query.context))

    def test_db_users(self):
        with app.test_request_context():
            start = time.clock()
            for i in range(1, 10000):
                user = ObjectMother.get_user()
                user.email = 'User' + str(i)
                db.session.add(user)
            db.session.commit()
            url = url_for('sadmin_users.index_view')
            self.app.get(url, follow_redirects=True)
            print time.clock() - start
            for query in get_debug_queries():
                if query.duration >= ProductionConfig.DATABASE_QUERY_TIMEOUT:
                    app.logger.warning("SLOW QUERY: %s\nParameters: %s\nDuration: %fs\nContext: %s\n" % (
                        query.statement, query.parameters, query.duration, query.context))


    def tearDown(self):
        with app.test_request_context():
            db.drop_all()


if __name__ == '__main__':
    unittest.main()
