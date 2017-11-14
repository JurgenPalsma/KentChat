#!/usr/bin/env python

# Copyright 2016 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START imports]
import os
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb

import jinja2
import webapp2
from webapp2_extras import json

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)
# [END imports]


class User(ndb.Model):
    """Sub model for representing an author."""
    identity = ndb.StringProperty(indexed=False)
    email = ndb.StringProperty(indexed=False)
    name = ndb.StringProperty(indexed=False)


class Welcome(webapp2.RequestHandler):  # Handler for GET '/'

    def get(self):
        self.response.content_type = 'application/json'
        obj = {
        'success': 'true',
        "message": "Welcome to KentChat API!"
        }
        self.response.write(json.encode(obj))


class Registration(webapp2.RequestHandler):  # Registration handler

    def get(self):
        self.response.content_type = 'application/json'
        obj = {
        'success': 'false',
        "message": "Not implemented yet"
        }
        self.response.write(json.encode(obj))


class Authentication(webapp2.RequestHandler):  # Auth handler

    def get(self):
        self.response.content_type = 'application/json'
        obj = {
        'success': 'false',
        "message": "Not implemented yet"
        }
        self.response.write(json.encode(obj))



# [START app] - Declare Routes with url and handler classes
app = webapp2.WSGIApplication([
    ('/', Welcome),
    ('/register', Registration),
    ('/authenticate', Authentication),
], debug=True)
# [END app]
