import sys
sys.path.append('..')

from google.appengine.ext import ndb
import webapp2
from webapp2_extras import json

from models import User
from utils import returns_json, fallback_param_to_req, get_params_from_request, treat_empty_string_as_none

def user_not_found(self, user_id=None):
    print('User not found {}'.format(': {}'.format(user_id) if user_id is not None else ''))
    self.abort(404)

def get_one_user(self, user_id):
    try:
        user = ndb.Key(urlsafe=user_id).get()
        if user is None:
            user_not_found(self, user_id=user_id)
        else:
            return user
    except Exception as e:
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

    @returns_json
    def post(self):
        user = User()
        user.email = self.request.get('email')
        user.name = self.request.get('name')
        print('POST on /users: {}'.format(user))

        user.put()
        self.response.write(json.encode(user.to_dict()))

    @treat_empty_string_as_none('user_id')
    @fallback_param_to_req('user_id')
    @returns_json
    def put(self, user_id=None):
        # Retrieve user
        if user_id is None:
            return user_not_found(self, user_id=user_id)
        else:
            user = get_one_user(self, user_id)

        # edit user
        user_modifs = get_params_from_request(self, 'email', 'name')

        if user_modifs['email'] is not None:
            user.email = user_modifs['email']
        if user_modifs['name'] is not None:
            user.name = user_modifs['name']

        user.put()
        self.response.write(json.encode(user.to_dict()))

    @treat_empty_string_as_none('user_id')
    @fallback_param_to_req('user_id')
    @returns_json
    def delete(self, user_id=None):
        if user_id is None:
            user_not_found(self, user_id=user_id)

        user = get_one_user(self, user_id)
        user.key.delete()
        res = {'message': 'User successfully deleted.'}
        self.response.write(json.encode(res))
