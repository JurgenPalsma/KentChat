import unittest
import webapp2

import json

from setups import setUp, tearDown

from testutils import assert_json, assert_success, assert_error

from google.appengine.ext import ndb

import sys
if '..' not in sys.path:
    sys.path.append('..')

from models import Conversation, User

class TestConversations(unittest.TestCase):
    setUp = setUp
    tearDown = tearDown

    def test_post_auth(self):
        user_key_1 = ndb.Key(User, 1)

        auth_post = {'email': 'kentuser1@gmail.com', 'password': 'password_1'}

        response = self.app.post('/auth', auth_post)

        assert_success(self, response)
        assert_json(self, response)

        result = json.loads(response.normal_body)

        self.assertEqual(result['token'], 'token_1')
        self.assertEqual(result['key'], user_key_1.urlsafe())
