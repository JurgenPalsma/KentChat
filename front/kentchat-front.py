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
        if self.session['user-token']:
            self.redirect("/chat")
        else:
            template_values = {
                "ph_password": "password",
                "ph_mail": "example@kent.ac.uk"
            }
            template = JINJA_ENVIRONMENT.get_template('./views/login.html')
            self.response.write(template.render(template_values))


class ChatPage(BaseHandler):

    def get(self):
        print("GET /chat")
        template_values = {}
        template = JINJA_ENVIRONMENT.get_template('./views/index.html')
        self.response.write(template.render(template_values))


class LoginController(BaseHandler):

    def post(self):
        print("GET /login")
        url = API_URL + "/auth"

        if self.request.get('email') and self.request.get('password'):
            data = dict(email=self.request.get('email'), password=self.request.get('password'))
            self.session['user-email'] = self.request.get('email')

        else:
            data = dict(email="joe@kent.ac.uk", password="pass")
            self.session['user-name'] = 'joe'
            self.session['user-email'] = 'joe@kent.ac.uk'

        response = requests.post(url, data=data, allow_redirects=True)

        if response.status_code == 200:
            data = json.loads(response.content)
            self.session['user-token'] = data['token']
            self.redirect("/chat")
        else:
            template_values = {
                "ph_password": "bad password",
                "ph_mail": "example@kent.ac.uk"
            }
            template = JINJA_ENVIRONMENT.get_template('./views/login.html')
            self.response.write(template.render(template_values))


class RegistrationController(BaseHandler):

    def post(self):
        print("1.GET /register")
        url = API_URL + "/users"

        if self.request.get('email') and self.request.get('password') \
                and self.request.get('username'):
            data = dict(name=self.request.get('username'),
                        email=self.request.get('email'),
                        password=self.request.get('password'))
            print("SUCCESS")
        else:
            data = dict(name='joe', email='joe@kent.ac.uk', password="pass")

        response = requests.post(url, data=data, allow_redirects=True)
        if response.status_code == 200:
            data = json.loads(response.content)
            self.session['user-key'] = data['key']
            self.response.write(self.session.get('user-key'))

        else:
            self.response.write(response.status_code)



config = {}
config['webapp2_extras.sessions'] = {
    'secret_key': 'my_super_secret_key',
}

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/login', LoginController),
    ('/register', RegistrationController),
    ('/chat', ChatPage),

], config=config,
    debug=True)
