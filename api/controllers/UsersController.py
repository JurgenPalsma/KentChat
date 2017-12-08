import sys
if '..' not in sys.path:
    sys.path.append('..')

from google.appengine.ext import ndb
import webapp2
from webapp2_extras import json

from models import User
from utils import returns_json, fallback_param_to_req, get_params_from_request, treat_empty_string_as_none, request_post_require

from AuthController import generate_password_hash, require_auth_token, auth_error

def user_not_found(self, user_id=None, *args, **kwargs):
    if user_id is not None:
        self.abort(404, 'User not found: {}'.format(user_id), *args, **kwargs)
    else:
        self.abort(404, *args, **kwargs)

# Get one conversation.
# If the auth token is provided, checks if the user corresponds to the auth_token
def get_one_user(self, user_id, auth_token=None):
    print('getting user {}'.format(user_id))
    user = ndb.Key(urlsafe=user_id).get()
    if user is None:
        user_not_found(self, user_id=user_id)
    else:
        if auth_token is not None: # If auth token has been given, check that it is the correct user. Else, we don't care
            user_by_token = User.get_by_auth_token(auth_token)
            if user is not user_by_token:
                auth_error(self)
            else:
                 return user
        else:
            return user
    user_not_found(self, user_id=user_id)

class UsersController(webapp2.RequestHandler):

    @treat_empty_string_as_none('user_id')
    @fallback_param_to_req('user_id')
    @returns_json
    def get(self, user_id=None):
        print('GET on /users/{}'.format(user_id))
        if user_id is None: # Return the list of users
            res = [u.to_dict() for u in User.query().order(User.name)]
        else: # Return one user
            user = get_one_user(self, user_id)
            res = user.to_dict()

        self.response.write(json.encode(res))

    @request_post_require('name', 'email', 'password')
    @returns_json
    def post(self):
        user = User()
        user.email = self.request.get('email')
        user.name = self.request.get('name')
        user.password = generate_password_hash(self.request.get('password'))

        print('POST on /users: {}'.format(user))

        user.put()
        self.response.write(json.encode(user.to_dict()))

    @require_auth_token
    @treat_empty_string_as_none('user_id')
    @fallback_param_to_req('user_id')
    @returns_json
    def put(self, user_id=None, auth_token=None):
        # Retrieve user
        if user_id is None:
            return user_not_found(self, user_id=user_id)
        else:
            user = get_one_user(self, user_id, auth_token=auth_token)

        # edit user
        user_modifs = get_params_from_request(self, 'email', 'name')

        if user_modifs['email'] is not None:
            user.email = user_modifs['email']
        if user_modifs['name'] is not None:
            user.name = user_modifs['name']

        user.put()
        self.response.write(json.encode(user.to_dict()))

    @require_auth_token
    @treat_empty_string_as_none('user_id')
    @fallback_param_to_req('user_id')
    @returns_json
    def delete(self, user_id=None, auth_token=None):
        if user_id is None:
            user_not_found(self, user_id=user_id)

        user = get_one_user(self, user_id, auth_token=auth_token)
        user.key.delete()
        res = {'message': 'User successfully deleted.'}
        self.response.write(json.encode(res))


class MeController(webapp2.RequestHandler):
    @require_auth_token
    @returns_json
    def get(self, auth_token=None):
        self.response.write(json.encode(User.get_by_auth_token(auth_token).to_dict()))
