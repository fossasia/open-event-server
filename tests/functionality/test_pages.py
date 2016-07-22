# -*- coding: utf-8 -*-
from datetime import datetime
import unittest

from tests.setup_database import Setup
from tests.utils import OpenEventTestCase
from app import current_app as app
from flask import url_for, request
import requests
from tests.auth_helper import register, login
from jinja2 import TemplateNotFound

class TestPagesUrls(OpenEventTestCase):

    def setUp(self):
        self.app = Setup.create_app()

    def test_event_name(self):
        """Tests all urls with GET method"""
        with app.test_request_context():

            for rule in app.url_map.iter_rules():
                methods = ','.join(rule.methods)
                if "<" not in str(rule)  and\
                        "favicon" not in str(rule) and\
                        "check_email" not in str(rule) and \
                        "set_role" not in str(rule) and \
                        "GET" in methods:
                    try:
                        status_code = self.app.get(request.url[:-1] + str(rule).replace('//', '/'),
                                                   follow_redirects=True).status_code
                        print str(rule), status_code, rule.endpoint
                        if 'api' in str(rule):
                            self.assertTrue(status_code in [200, 302, 401, 404])
                        else:
                            self.assertTrue(status_code in [200, 302, 401])
                    except TemplateNotFound:
                        pass
                    except AttributeError:
                        pass

if __name__ == '__main__':
    unittest.main()
