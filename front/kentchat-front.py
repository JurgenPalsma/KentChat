#!/usr/bin/env python
import os
import urllib

import jinja2
import webapp2
from google.appengine.api import users
from google.appengine.ext import ndb

import random
import requests
import requests_toolbelt.adapters.appengine

# Use the App Engine Requests adapter. This makes sure that Requests uses
# URLFetch.
requests_toolbelt.adapters.appengine.monkeypatch()
API_URL = "http://localhost:5010"

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class MainPage(webapp2.RequestHandler):  # Handler for GET '/'

    def get(self):
        template_values = {
            'user': "john",
        }
        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))



class LoginController(webapp2.RequestHandler):  # Handler for GET '/'

    def get(self):
        print("POST /login")

        url = API_URL + "/users"
        data = dict(name='joe', email='joe@kent.ac.uk', password="pass")

        response = requests.post(url, data=data, allow_redirects=True)
        self.response.write(response.text)

    def post(self):
        print("POST /login")

        url = API_URL + "/users"
        data = dict(name='joe', email='joe@kent.ac.uk', password="pass")

        response = requests.post(url, data=data, allow_redirects=True)
        self.response.write(response.read())




app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/login', LoginController),
], debug=True)
