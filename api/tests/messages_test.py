import unittest
import webapp2

import json

from setups import setUp, tearDown

from testutils import assert_json, assert_success, assert_error, auth_headers

from google.appengine.ext import ndb

import sys
if '..' not in sys.path:
    sys.path.append('..')

from models import Message, Conversation, User

class TestMessages(unittest.TestCase):
    setUp = setUp
    tearDown = tearDown

    def test_get_all_in_conv(self):
        conv_key_1 = ndb.Key(Conversation, 11)
        user_key_1 = ndb.Key(User, 1)
        user_key_2 = ndb.Key(User, 2)

        response = self.app.get('/conversations/{}/messages'.format(conv_key_1.urlsafe()), headers=auth_headers('token_1'))

        assert_success(self, response)
        assert_json(self, response)

        messages = json.loads(response.normal_body)

        self.assertEqual(len(messages), 2)
        message_1, message_2 = messages

        self.assertEqual(message_1['content'], 'message 1')
        self.assertEqual(message_1['user'], user_key_1.urlsafe())
        key_1 = ndb.Key(urlsafe=message_1['key'])
        self.assertEqual(key_1.id(), 101)

        self.assertEqual(message_2['content'], 'message 2')
        self.assertEqual(message_2['user'], user_key_2.urlsafe())
        key_2 = ndb.Key(urlsafe=message_2['key'])
        self.assertEqual(key_2.id(), 102)


    def test_get_one(self):
        key = ndb.Key(Conversation, 11, Message, 101)
        user_key_1 = ndb.Key(User, 1)

        response = self.app.get('/messages/{}'.format(key.urlsafe()), headers=auth_headers('token_1'))

        assert_success(self, response)
        assert_json(self, response)

        message = json.loads(response.normal_body)

        self.assertEqual(message['content'], 'message 1')
        self.assertEqual(message['user'], user_key_1.urlsafe())
        key_obtained = ndb.Key(urlsafe=message['key'])
        self.assertEqual(key, key_obtained)


    def test_put_one(self):
        key = ndb.Key(Conversation, 11, Message, 101)
        user_key_1 = ndb.Key(User, 1)

        response = self.app.put('/messages/{}'.format(key.urlsafe()), {'content': 'oops, I edited the message'}, headers=auth_headers('token_1'))

        assert_success(self, response)
        assert_json(self, response)

        message = json.loads(response.normal_body)

        self.assertEqual(message['content'], 'oops, I edited the message')
        self.assertEqual(message['user'], user_key_1.urlsafe())
        key_obtained = ndb.Key(urlsafe=message['key'])
        self.assertEqual(key, key_obtained)

    def test_delete_one(self):
        key = ndb.Key(Conversation, 11, Message, 102)
        conv_key_1 = ndb.Key(Conversation, 11)

        response_delete = self.app.delete('/messages/{}'.format(key.urlsafe()), headers=auth_headers('token_2'))

        assert_success(self, response_delete)
        assert_json(self, response_delete)

        response_get = self.app.get('/conversations/{}/messages'.format(conv_key_1.urlsafe()), headers=auth_headers('token_2'))

        messages = json.loads(response_get.normal_body)

        for message in messages:
            self.assertNotEqual(message['key'], key.urlsafe())
