#!/usr/bin/env python
import os
import urllib

import jinja2
import webapp2
from webapp2_extras import sessions # for cookies
import datetime

from functools import wraps


from google.appengine.api import users
from google.appengine.ext import ndb

import time
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

    def api_auth(self, email, password):
        url = API_URL + "/auth"
        data = dict(email=email, password=password)
        self.session['user-email'] = self.request.get('email')
        response = requests.post(url, data=data, allow_redirects=True)
        self.response.write(response.content)
        data = json.loads(response.content)
        self.session['user-token'] = data['token']
        return response


    # Make sure user is logged in
    @staticmethod
    def logged_in(method):
        @wraps(method)
        def wrapper(self, *args, **kwargs):
            if "user-key" in self.session:
                if not self.session["user-key"] == "":
                    method(self, *args, **kwargs)
                else:
                    self.redirect("/")
            else:
                self.redirect("/")
        return wrapper


    def api_get_conversations(self):
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
        self.session["conversations"] = conversations
        return conversations

    def api_get_nonfriends(self):
        if "user-key" not in self.session or "users" not in self.session:
            url = API_URL + "/users"
            response = requests.get(url, allow_redirects=True)
            data = json.loads(response.content)
            self.session["users"] = data
            for user in data:
                if self.session['user-email'] in user["email"]:
                    self.session['user-key'] = user["key"]
                    time.sleep(0.1)
            print("HI")

        url = API_URL + "/users/" + self.session['user-key'] + "/nonfriends"
        response = requests.get(url, allow_redirects=True)
        if response.status_code != 200:
            print(response.status_code)
            print(response.content)
            return
        data = json.loads(response.content)
        self.session["nonfriends"] = data

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
            if other_user_key == "":
                conv["name"] = "Yourself"
                return conv



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

    @BaseHandler.logged_in
    def get(self):
        print("GET /chat")
        self.api_get_nonfriends()
        self.api_get_conversations()
        template_values = {
            "conversations": self.session["conversations"],
            "users": self.session["users"],
            "nonfriends": self.session["nonfriends"]
        }
        template = JINJA_ENVIRONMENT.get_template('./views/index.html')
        self.response.write(template.render(template_values))


class AddConvController(BaseHandler):

    def get(self):
        url = API_URL + "/conversations"
        data = {'users_ids': json.dumps([self.session["user-key"],
                                         self.request.get("other_user_key")])}
        response = requests.post(url, data=data,
                                 allow_redirects=True)
        self.api_get_conversations()
        time.sleep(0.5)
        self.redirect("/chat")


class ConversationController(BaseHandler):

    def format_time(self, messages):
        for message in messages:
            message["post_time"] = datetime.datetime.fromtimestamp(int(message["post_time"])).strftime("%H:%M")
        return messages

    def get(self):

        url = API_URL + "/conversations/" + self.request.get("conversation_key") + "/messages"
        response = requests.get(url, headers={'authorization': "Bearer " + self.session['user-token']}, allow_redirects=True)
        if response.status_code == 200:
            messages = json.loads(response.content)
        else:
            return self.response.write(response.content)
        messages = self.format_time(messages)
        if "user-key" not in self.session or "users" not in self.session:
            url = API_URL + "/users"
            response = requests.get(url, allow_redirects=True)
            data = json.loads(response.content)
            self.session["users"] = data
            for user in data:
                if self.session['user-email'] in user["email"]:
                    self.session['user-key'] = user["key"]
        self.api_get_nonfriends()
        self.api_get_conversations()
        template_values = {
            "conversations": self.session["conversations"],
            "messages": messages,
            "current_conversation_key": self.request.get("conversation_key"),
            "users": self.session["users"],
            "self_key": self.session["user-key"],
            "nonfriends": self.session["nonfriends"]
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
            self.redirect("/chat")


class LoginController(BaseHandler):

    def post(self):
        print("GET /login")
        url = API_URL + "/auth"

        if self.request.get('email') and self.request.get('password'):
            auth_response = self.api_auth(self.request.get('email'), self.request.get('password'))
            if auth_response.status_code == 200:
                if "user-key" not in self.session or "users" not in self.session:
                    url = API_URL + "/users"
                    response = requests.get(url, allow_redirects=True)
                    data = json.loads(response.content)
                    self.session["users"] = data
                    for user in data:
                        if self.session['user-email'] in user["email"]:
                            self.session['user-key'] = user["key"]

                self.redirect("/chat")
                return
        template_values = {
            "ph_password": "bad password",
            "ph_mail": "example@kent.ac.uk"
        }
        template = JINJA_ENVIRONMENT.get_template('./views/login.html')
        self.response.write(template.render(template_values))

class LogoutController(BaseHandler):

    def get(self):
        print("GET /logout")
        self.session["user-key"] = ""
        self.redirect("/")


class RegistrationController(BaseHandler):

    def post(self):
        print("GET /register")
        url = API_URL + "/users"

        if self.request.get('email') and self.request.get('password') \
                and self.request.get('username'):
            password = self.request.get('password')
            email = self.request.get('email')

            data = dict(name=self.request.get('username'),
                        email=email,
                        password=password)
            response = requests.post(url, data=data, allow_redirects=True)
            time.sleep(0.1)

            if response.status_code == 200:
                data = json.loads(response.content)
                print("Try to login after registration)")
                self.session['user-key'] = data['key']

                auth_response = self.api_auth(email, password)

                if auth_response.status_code == 200:
                    self.redirect("/chat")
                    return
                else:
                    self.response.write("auth post registration failed")
                    return
        self.redirect("/?redirect=registration_failed")




config = {}
config['webapp2_extras.sessions'] = {
    'secret_key': 'my_super_secret_key',
}

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/login', LoginController),
    ('/logout', LogoutController),
    ('/register', RegistrationController),
    ('/chat', ChatPage),
    ('/conversation', ConversationController),
    ('/send_message', SendController),
    ('/add_conversation', AddConvController),

], config=config,
    debug=True)
