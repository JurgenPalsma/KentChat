import sys
if '..' not in sys.path:
    sys.path.append('..')

from google.appengine.ext import ndb
import webapp2
from webapp2_extras import json, security

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

class LoginController(webapp2.RequestHandler):

    @request_post_require('email', 'password')
    @returns_json
    def post(self):
        email = self.request.get('email')
        password = self.request.get('password')

        users = [user for user in User.query(User.email == email) if security.check_password_hash(password, user.password)]
        if len(users) is 0:
            auth_error(self, 'Email or Password not found/matching')

        user = users[0]

        token = user.add_new_token()
        self.response.write(json.encode({'token': token, 'key': users[0].key.urlsafe()}))

class LogoutController(webapp2.RequestHandler):

    @require_auth_token
    @returns_json
    def post(self, auth_token=None):

        user = User.get_by_auth_token(auth_token)
        success = user.remove_token(auth_token)

        if success:
            self.response.write(json.encode({'message': 'Have a good day'}))
        else:
            self.abort(403, 'Could not logout')
