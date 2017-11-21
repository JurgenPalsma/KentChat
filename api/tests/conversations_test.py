import unittest
import webapp2

import json

from setups import setUp, tearDown

from testutils import assert_json, assert_success, assert_error, auth_headers

from google.appengine.ext import ndb

import sys
if '..' not in sys.path:
    sys.path.append('..')

from models import Conversation, User

class TestConversations(unittest.TestCase):
    setUp = setUp
    tearDown = tearDown

    def test_get_all(self):
        user_key_1 = ndb.Key(User, 1)
        user_key_2 = ndb.Key(User, 2)

        response = self.app.get('/conversations', headers=auth_headers('token_1'))

        assert_success(self, response)
        assert_json(self, response)

        conversations = json.loads(response.normal_body)

        self.assertEqual(len(conversations), 2)
        conversation_1, conversation_2 = conversations

        self.assertEqual(conversation_1['name'], 'super conv 1')
        self.assertEqual(conversation_1['users'], [user_key_1.urlsafe(), user_key_2.urlsafe()])
        key_1 = ndb.Key(urlsafe=conversation_1['key'])
        self.assertEqual(key_1.id(), 11)

        self.assertIsNone(conversation_2['name'])
        self.assertEqual(conversation_2['users'], [user_key_2.urlsafe(), user_key_2.urlsafe()])
        key_2 = ndb.Key(urlsafe=conversation_2['key'])
        self.assertEqual(key_2.id(), 12)


    def test_get_one(self):
        user_key_1 = ndb.Key(User, 1)
        user_key_2 = ndb.Key(User, 2)

        key = ndb.Key(Conversation, 11)

        response = self.app.get('/conversations/{}'.format(key.urlsafe()))

        assert_success(self, response)
        assert_json(self, response)

        conversation = json.loads(response.normal_body)

        self.assertEqual(conversation['users'], [user_key_1.urlsafe(), user_key_2.urlsafe()])
        key_obtained = ndb.Key(urlsafe=conversation['key'])
        self.assertEqual(key, key_obtained)

    def test_get_all_in_user(self):
        user_key_1 = ndb.Key(User, 1)
        user_key_2 = ndb.Key(User, 2)

        response = self.app.get('/users/{}/conversations'.format(user_key_1.urlsafe()), headers=auth_headers('token_1'))

        assert_success(self, response)
        assert_json(self, response)

        conversations = json.loads(response.normal_body)

        self.assertEqual(len(conversations), 1)
        conversation_1 = conversations[0]

        self.assertEqual(conversation_1['name'], 'super conv 1')
        self.assertEqual(conversation_1['users'], [user_key_1.urlsafe(), user_key_2.urlsafe()])
        key_1 = ndb.Key(urlsafe=conversation_1['key'])
        self.assertEqual(key_1.id(), 11)


    def test_put_one(self):

        key = ndb.Key(Conversation, 11)
        user_key_1 = ndb.Key(User, 1)
        user_key_2 = ndb.Key(User, 2)

        conv_edit = {'users': json.dumps([user_key_1.urlsafe(), user_key_1.urlsafe()]) }

        response = self.app.put('/conversations/{}'.format(key.urlsafe()), conv_edit, headers=auth_headers('token_1'))

        assert_success(self, response)
        assert_json(self, response)

        conversation = json.loads(response.normal_body)

        self.assertEqual(conversation['users'], [user_key_1.urlsafe(), user_key_1.urlsafe()])
        key_obtained = ndb.Key(urlsafe=conversation['key'])
        self.assertEqual(key, key_obtained)

    def test_post_one(self):
        user_key_1 = ndb.Key(User, 1)
        user_key_2 = ndb.Key(User, 2)

        conversation = {'users_ids': json.dumps([user_key_1.urlsafe(), user_key_2.urlsafe()])}

        response = self.app.post('/conversations', conversation, headers=auth_headers('token_1'))

        assert_success(self, response)
        assert_json(self, response)

        conversation_result = json.loads(response.normal_body)

        self.assertEqual(conversation_result['users'], [user_key_1.urlsafe(), user_key_2.urlsafe()])
        self.assertIn('key', conversation_result)

    def test_delete_one(self):
        key = ndb.Key(Conversation, 11)

        response_delete = self.app.delete('/conversations/{}'.format(key.urlsafe()), headers=auth_headers('token_1'))

        assert_success(self, response_delete)
        assert_json(self, response_delete)

        response_get = self.app.get('/conversations')

        conversations = json.loads(response_get.normal_body)

        for conversation in conversations:
            self.assertNotEqual(conversation['key'], key.urlsafe())
