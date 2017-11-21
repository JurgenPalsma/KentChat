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

        if self.session.get('user-token'):
            template_values = {
            'name': self.session.get('user-name'),
            'email': self.session.get('user-email'),
            'token': self.session.get('user-token'),
            'key': self.session.get('user-key')
            }
            self.response.write("hi, you're logged in with " + template_values.__str__())
        else:
            self.response.write("You are not logged in")



class LoginController(BaseHandler):

    def get(self):
        print("GET /login")
        url = API_URL + "/auth"

        if self.request.get('email') and self.request.get('password') \
                and self.request.get('remember') and self.request.get('login'):
            data = dict(email=self.request.get('email'), password=self.request.get('password'))
            self.session['user-email'] = self.request.get('email')

        else:
            data = dict(email="joe@kent.ac.uk", password="password")
            self.session['user-name'] = 'joe'
            self.session['user-email'] = 'joe@kent.ac.uk'

        response = requests.post(url, data=data, allow_redirects=True)
        data = json.loads(response.content)
        self.session['user-token'] = data['token']
        self.response.write(self.session.get('user-token'))


class RegistrationController(BaseHandler):

    def get(self):
        print("GET /register")
        url = API_URL + "/users"

        if self.request.get('email') and self.request.get('password') \
                and self.request.get('remember') and self.request.get('login') \
                and self.request.get('username'):
            data = dict(name=self.request.get('username'),
                        email=self.request.get('email'),
                        password=self.request.get('password'))
        else:
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
