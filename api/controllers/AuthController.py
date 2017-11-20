import sys
if '..' not in sys.path:
    sys.path.append('..')

from google.appengine.ext import ndb
import webapp2
from webapp2_extras import json

from random import choice

from models import User
from utils import returns_json, fallback_param_to_req, get_params_from_request, treat_empty_string_as_none, request_post_require

def generate_token(size=16):
    alphabet = 'abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    return reduce(lambda a, b: str(a) + str(b), [choice(alphabet) for _ in range(size)])

def auth_error(self):
    self.abort(403)

class AuthController(webapp2.RequestHandler):

    @request_post_require('email', 'password')
    @returns_json
    def post(self):
        email = self.request.get('email')
        password = self.request.get('password')

        users = list(User.query(User.email == email, User.password == password))
        if len(users) is 0:
            auth_error(self)

        self.response.write(json.encode({'token': users[0].token}))
