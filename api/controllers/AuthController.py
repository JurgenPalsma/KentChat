import sys
if '..' not in sys.path:
    sys.path.append('..')

from google.appengine.ext import ndb
import webapp2
from webapp2_extras import json, security

from random import choice
from functools import wraps

from models import User
from utils import returns_json, fallback_param_to_req, get_params_from_request, treat_empty_string_as_none, request_post_require

def auth_error(self, *args, **kwargs):
    self.abort(403, *args, **kwargs)

# decorator that checks that the request has an auth token, and that this token represents an user.
def require_auth_token(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        if 'authorization' not in self.request.headers:
            auth_error(self, 'No authorization header found: {}'.format(dict(self.request.headers)))
        else:
            auth_header = self.request.headers['authorization']
            try:
                auth_type, auth_token = auth_header.split(' ')
                print(auth_type, auth_token)
                if auth_type == 'Bearer' or auth_type == 'bearer':
                    if User.get_by_auth_token(auth_token) is not None:
                        method(self, auth_token=auth_token, *args, **kwargs)
                    else:
                        auth_error(self, 'Bad authorization token')
                else:
                    auth_error(self, 'Bad authorization method')
            except ValueError as e:
                auth_error(self)
    return wrapper

def generate_password_hash(raw_password):
    return security.generate_password_hash(raw_password, length=12)

def generate_token(size=16):
    alphabet = 'abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    return reduce(lambda a, b: str(a) + str(b), [choice(alphabet) for _ in range(size)])


class AuthController(webapp2.RequestHandler):

    @request_post_require('email', 'password')
    @returns_json
    def post(self):
        email = self.request.get('email')
        password = self.request.get('password')

        users = [user for user in User.query(User.email == email) if security.check_password_hash(password, user.password)]
        if len(users) is 0:
            auth_error(self, 'Email of Password not found/matching')

        self.response.write(json.encode({'token': users[0].token, 'key': users[0].key.urlsafe()}))
