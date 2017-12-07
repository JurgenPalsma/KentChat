import unittest
import webapp2

import json

from setups import setUp, tearDown

from testutils import assert_json, assert_success, assert_error, auth_headers

from google.appengine.ext import ndb

import sys
if '..' not in sys.path:
    sys.path.append('..')

from models import User

class TestUsers(unittest.TestCase):
    setUp = setUp
    tearDown = tearDown


    def test_get(self):
        key = ndb.Key(User, 1)

        response = self.app.get('/users/{}/nonfriends'.format(key.urlsafe()))

        assert_success(self, response)
        assert_json(self, response)

        users = json.loads(response.normal_body)

        self.assertEqual(len(users), 1)
        user_3 = users[0]

        self.assertEqual(user_3['name'], 'kent user 3')
        self.assertEqual(user_3['email'], 'kentuser3@gmail.com')
        key_3 = ndb.Key(urlsafe=user_3['key'])
        self.assertEqual(key_3.id(), 3)
