#!/usr/bin/env python
import os
import urllib

import jinja2
import webapp2
from webapp2_extras import sessions # for cookies


from google.appengine.api import users
from google.appengine.ext import ndb

import random
import requests
import requests_toolbelt.adapters.appengine
import json

# Use the App Engine Requests adapter. This makes sure that Requests uses
# URLFetch.
requests_toolbelt.adapters.appengine.monkeypatch()
API_URL = "http://localhost:5010"

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


class BaseHandler(webapp2.RequestHandler):              # taken from the webapp2 extra session example
    def dispatch(self):                                 # override dispatch
        # Get a session store for this request.
        self.session_store = sessions.get_store(request=self.request)

        try:
            # Dispatch the request.
            webapp2.RequestHandler.dispatch(self)       # dispatch the main handler
        finally:
            # Save all sessions.
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):
        # Returns a session using the default cookie key.
        return self.session_store.get_session()


class MainPage(BaseHandler):

    def get(self):
        print("GET /")
        template_values = {
            'user': "john",
            'foo': self.session.get('user-key')
        }
        template = JINJA_ENVIRONMENT.get_template('index.html')
        #self.response.write(template.render(template_values))
        self.response.write("hi")


class LoginController(BaseHandler):

    def get(self):
        print("GET /login")

        url = API_URL + "/auth"
        data = dict(name='joe', email='joe@kent.ac.uk', password="pass")

        response = requests.post(url, data=data, allow_redirects=True)
        data = json.loads(response.content)
        self.session['user-token'] = data['token']

        self.response.write(self.session.get('user-token'))


class RegistrationController(BaseHandler):

    def get(self):
        print("GET /register")

        url = API_URL + "/users"
        data = dict(name='joe', email='joe@kent.ac.uk', password="pass")

        response = requests.post(url, data=data, allow_redirects=True)
        data = json.loads(response.content)
        self.session['user-key'] = data['key']

        self.response.write(self.session.get('user-key'))


config = {}
config['webapp2_extras.sessions'] = {
    'secret_key': 'my_super_secret_key',
}

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/login', LoginController),
    ('/register', RegistrationController)
], config=config,
    debug=True)
