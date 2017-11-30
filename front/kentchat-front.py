#!/usr/bin/env python
import os
import urllib

import jinja2
import webapp2
from webapp2_extras import sessions # for cookies
import datetime


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
            "ph_password": "password",
            "ph_mail": "example@kent.ac.uk"
        }
        template = JINJA_ENVIRONMENT.get_template('./views/login.html')
        self.response.write(template.render(template_values))




class ChatPage(BaseHandler):

    def set_conv_name(self, conv, users):
        other_user_key = ""
        if len(conv["users"]) > 2:
            conv["name"] = "multiple users"
            return conv
        for u in conv["users"]:
            if u != self.session['user-key']:
                other_user_key = u
        for user in users:
            if other_user_key == user["key"]:
                conv["name"] = user["name"]
                return conv

    def get(self):
        print("GET /chat")

        if "user-key" not in self.session or "users" not in self.session:
            url = API_URL + "/users"
            response = requests.get(url, allow_redirects=True)
            data = json.loads(response.content)
            self.session["users"] = data
            for user in data:
                if self.session['user-email'] in user["email"]:
                    self.session['user-key'] = user["key"]

        conversations = []
        url = API_URL + "/conversations"
        response = requests.get(url, allow_redirects=True)
        data = json.loads(response.content)
        for conv in data:
            if self.session["user-key"] in conv["users"]:
                conversations.append(conv)

        url = API_URL + "/users"
        response = requests.get(url, allow_redirects=True)
        users = json.loads(response.content)

        # find name of user that is not you
        for conv in conversations:
            conv = self.set_conv_name(conv, users)

        self.session["conversations"]= conversations


        template_values = {
            "conversations": conversations,
            "users": self.session["users"]
        }
        template = JINJA_ENVIRONMENT.get_template('./views/index.html')
        self.response.write(template.render(template_values))


class AddConvController(BaseHandler):

    def get(self):
        url = API_URL + "/conversations"
        data = {'users_ids': json.dumps([self.session["user-key"],
                                         self.request.get("other_user_key")])}
        print(data)
        response = requests.post(url, data=data,
                                 allow_redirects=True)
        print(response.content)
        self.redirect("/chat")


class ConversationController(BaseHandler):

    def format_time(self, messages):
        for message in messages:
            message["post_time"] = datetime.datetime.fromtimestamp(int(message["post_time"])).strftime("%H:%M")
        return messages

    def get(self):

        url = API_URL + "/conversations/" + self.request.get("conversation_key") + "/messages"
        response = requests.get(url, headers={'authorization': "Bearer " + self.session['user-token']}, allow_redirects=True)
        if response.content:
            print("USER TOKEN::")
            print(self.session['user-token'])
            print(response.content)
            messages = json.loads(response.content)
        else:
            messages = []

        messages = self.format_time(messages)

        template_values = {
            "conversations": self.session["conversations"],
            "messages": messages,
            "current_conversation_key": self.request.get("conversation_key"),
            "users": self.session["users"]
        }
        template = JINJA_ENVIRONMENT.get_template('./views/index.html')
        self.response.write(template.render(template_values))


class SendController(BaseHandler):

    def post(self):
        url = API_URL + "/conversations/" + self.request.get("current_conversation_key") + "/messages"
        data = dict(content=self.request.get("message_content"))
        response = requests.post(url, data=data,
                      headers={'authorization': "Bearer " + self.session['user-token']},
                      allow_redirects=True)
        if response.status_code == 200:
            self.redirect("/conversation?conversation_key=" + self.request.get("current_conversation_key"))
        else:
            self.response.write(response.status_code)




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
    ('/conversation', ConversationController),
    ('/send_message', SendController),
    ('/add_conversation', AddConvController),

], config=config,
    debug=True)
