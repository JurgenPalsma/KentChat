import unittest
import webapp2

import json

from setups import setUp, tearDown

from testutils import assert_json, assert_success, assert_error

from google.appengine.ext import ndb

import sys
if '..' not in sys.path:
    sys.path.append('..')

from models import User

class TestUsers(unittest.TestCase):
    setUp = setUp
    tearDown = tearDown


    def test_get_all(self):
        response = self.app.get('/users')

        assert_success(self, response)
        assert_json(self, response)

        users = json.loads(response.normal_body)

        self.assertEqual(len(users), 2)
        user_1, user_2 = users

        self.assertEqual(user_1['name'], 'kent user 1')
        self.assertEqual(user_1['email'], 'kentuser1@gmail.com')
        key_1 = ndb.Key(urlsafe=user_1['key'])
        self.assertEqual(key_1.id(), 1)

        self.assertEqual(user_2['name'], 'kent user 2')
        self.assertEqual(user_2['email'], 'kentuser2@gmail.com')
        key_2 = ndb.Key(urlsafe=user_2['key'])
        self.assertEqual(key_2.id(), 2)


    def test_get_one(self):
        key = ndb.Key(User, 1)

        response = self.app.get('/users/{}'.format(key.urlsafe()))

        assert_success(self, response)
        assert_json(self, response)

        user = json.loads(response.normal_body)

        self.assertEqual(user['name'], 'kent user 1')
        self.assertEqual(user['email'], 'kentuser1@gmail.com')
        key_obtained = ndb.Key(urlsafe=user['key'])
        self.assertEqual(key, key_obtained)


    def test_put_one(self):
        key = ndb.Key(User, 1)

        response = self.app.put('/users/{}'.format(key.urlsafe()), {'name': 'JOHN CENA'})

        assert_success(self, response)
        assert_json(self, response)

        user = json.loads(response.normal_body)

        self.assertEqual(user['name'], 'JOHN CENA')
        self.assertEqual(user['email'], 'kentuser1@gmail.com')
        key_obtained = ndb.Key(urlsafe=user['key'])
        self.assertEqual(key, key_obtained)

    def test_post_one(self):
        user = {'name': 'user 3', 'email': 'kentuser3@gmail.com', 'password': 'password_3'}

        response = self.app.post('/users', user)

        assert_success(self, response)
        assert_json(self, response)

        user_result = json.loads(response.normal_body)

        self.assertEqual(user_result['name'], user['name'])
        self.assertEqual(user_result['email'], user['email'])
        self.assertIn('key', user_result)

    def test_delete_one(self):
        key = ndb.Key(User, 1)

        response_delete = self.app.delete('/users/{}'.format(key.urlsafe()))

        assert_success(self, response_delete)
        assert_json(self, response_delete)

        response_get = self.app.get('/users')

        users = json.loads(response_get.normal_body)

        for user in users:
            self.assertNotEqual(user['key'], key.urlsafe())
