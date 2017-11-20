#!/usr/bin/env python

# Copyright 2016 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START imports]
import os
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb

import webapp2
from webapp2_extras import json, routes
from models import User, Message, Conversation

from controllers import UsersController, UsersConversationsController, ConversationsController, MessagesController, AuthController

class Welcome(webapp2.RequestHandler):  # Handler for GET '/'

    def get(self):
        self.response.content_type = 'application/json'
        obj = {
        'success': 'true',
        'message': 'Welcome to KentChat API!'
        }
        self.response.write(json.encode(obj))


class Registration(webapp2.RequestHandler):  # Registration handler

    def get(self):
        self.response.content_type = 'application/json'
        obj = {
        'success': 'false',
        'message': 'Not implemented yet'
        }
        self.response.write(json.encode(obj))


class Authentication(webapp2.RequestHandler):  # Auth handler

    def get(self):
        self.response.content_type = 'application/json'
        obj = {
        'success': 'false',
        'message': 'Not implemented yet'
        }
        self.response.write(json.encode(obj))



# [START app] - Declare Routes with url and handler classes
app = webapp2.WSGIApplication([
    webapp2.Route('/', Welcome),
    webapp2.Route('/register', Registration),
    webapp2.Route('/authenticate', Authentication),
    webapp2.Route('/users', UsersController, name='users', methods=['GET', 'POST']),
    webapp2.Route(r'/users/<user_id:[^/]*>', UsersController, name='users', methods=['GET', 'PUT', 'DELETE']),
    webapp2.Route(r'/users/<user_id>/conversations<:/?>', UsersConversationsController, name='users_conversations', methods=['GET']),

    webapp2.Route('/conversations', ConversationsController, name='conversations', methods=['GET', 'POST']),
    webapp2.Route(r'/conversations/<conv_id:[^/]*>', ConversationsController, name='conversations', methods=['GET', 'PUT', 'DELETE']),

    webapp2.Route(r'/conversations/<conv_id>/messages', MessagesController, name='convesrsations_messages', methods=['GET', 'POST']),
    webapp2.Route(r'/conversations/<conv_id>/messages/', MessagesController, name='convesrsations_messages', methods=['GET', 'POST']),
    webapp2.Route(r'/messages/<msg_id:[^/]*>', MessagesController, name='messages', methods=['GET', 'PUT', 'DELETE']),

    webapp2.Route(r'/auth', AuthController, name='auth', methods=['POST']),
], debug=True)
# [END app]
