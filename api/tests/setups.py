#!/usr/bin/env python2.7

import sys
sys.path.append('..')

import unittest
import webapp2
import webtest

import datetime

from google.appengine.ext import ndb
from google.appengine.ext import testbed

from models import User, Conversation, Message

from kentchat import app

def add_users():
    User.allocate_ids(max=100)
    user_1 = User(email='kentuser1@gmail.com', name='kent user 1', id=1)
    user_2 = User(email='kentuser2@gmail.com', name='kent user 2', id=2)
    user_1.put()
    user_2.put()

def add_conversations():
    user_key_1 = ndb.Key(User, 1)
    user_key_2 = ndb.Key(User, 2)

    Conversation.allocate_ids(max=100)
    conv_1 = Conversation(users=[user_key_1, user_key_2], name='super conv 1', id=11)
    conv_2 = Conversation(users=[user_key_2, user_key_2], id=12)
    conv_1.put()
    conv_2.put()

def add_messages():
    conv_key_1 = ndb.Key(Conversation, 11)

    user_key_1 = ndb.Key(User, 1)
    user_key_2 = ndb.Key(User, 2)

    Message.allocate_ids(max=1000, parent=conv_key_1)
    msg_1 = Message(parent=conv_key_1, content='message 1', user=user_key_1, id=101)
    msg_2 = Message(parent=conv_key_1, content='message 2', user=user_key_2, id=102)
    msg_1.post_time = datetime.datetime.utcfromtimestamp(1483286400)
    msg_2.post_time = datetime.datetime.utcfromtimestamp(1483291800)

    msg_1.put()
    msg_2.put()


def setUp(self):
    self.testbed = testbed.Testbed()
    self.testbed.activate()
    self.testbed.init_datastore_v3_stub()
    self.testbed.init_memcache_stub()

    ndb.get_context().clear_cache()

    add_users()
    add_conversations()
    add_messages()

    self.app = webtest.TestApp(app)


def tearDown(self):
    self.testbed.deactivate()
