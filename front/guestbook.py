#!/usr/bin/env python
import os
import urllib

import jinja2
import webapp2
from google.appengine.api import users
from google.appengine.ext import ndb

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


class MainPage(webapp2.RequestHandler):  # Handler for GET '/'

    def get(self):
        template_values = {
            'user': "john",
        }
        template = JINJA_ENVIRONMENT.get_template('login.html')
        self.response.write(template.render(template_values))

#class Login(webapp2.RequestHandler): 

app = webapp2.WSGIApplication([
    ('/', MainPage),
	('/sign', MainPage),
	('/xxx', MainPage),
], debug=True)
