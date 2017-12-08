import unittest
import webapp2
import webtest

import json

from setups import setUp, tearDown

from testutils import assert_json, assert_success, assert_error, auth_headers

from google.appengine.ext import ndb

import sys
if '..' not in sys.path:
    sys.path.append('..')

from models import Conversation, User

class TestAuth(unittest.TestCase):
    setUp = setUp
    tearDown = tearDown

    def test_login(self):
        user_key_1 = ndb.Key(User, 1)

        auth_post = {'email': 'kentuser1@gmail.com', 'password': 'password_1'}

        response = self.app.post('/auth', auth_post)

        assert_success(self, response)
        assert_json(self, response)

        result = json.loads(response.normal_body)

        self.assertTrue('token' in result)
        self.assertEqual(result['key'], user_key_1.urlsafe())

    def post_logout(self):
        response = self.app.post('/logout', headers=auth_headers('token_1'))

        assert_success(self, response)
        assert_json(self, response)

        response_me = self.app.get('/me', headers=auth_headers('token_1'), expect_errors=True)
        assertError(self, response_me.status_int, error_code=403)
