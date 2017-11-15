import sys
sys.path.append('..')

from google.appengine.ext import ndb
import webapp2
from webapp2_extras import json

from models import User
from utils import entity_to_dict, returns_json, fallback_param_to_req, get_params_from_request, treat_empty_string_as_none

def user_not_found(self):
    self.abort(404)

def get_one_user(self, key):
    try:
        user = ndb.Key(urlsafe=key).get()
        if user is None:
            user_not_found(self)
        else:
            return user
    except Exception as e:
        user_not_found(self)

class UserController(webapp2.RequestHandler):

    @treat_empty_string_as_none('key')
    @fallback_param_to_req('key')
    @returns_json
    def get(self, key=None):
        print('GET on /users/{}'.format(key))
        if key is None: # Return the list of users
            res = [entity_to_dict(u) for u in User.query().order(User.name)]
        else: # Return one user
            user = get_one_user(self, key)
            res = entity_to_dict(user)

        self.response.write(json.encode(res))

    @returns_json
    def post(self):
        user = User()
        user.email = self.request.get('email')
        user.name = self.request.get('name')
        print('POST on /users: {}'.format(user))

        user.put()
        self.response.write(json.encode(entity_to_dict(user)))

    @treat_empty_string_as_none('key')
    @fallback_param_to_req('key')
    @returns_json
    def put(self, key=None):
        # Retrieve user
        if key is None:
            return user_not_found(self)
        else:
            user = get_one_user(self, key)

        # edit user
        user_modifs = get_params_from_request(self, 'email', 'name')

        if user_modifs['email'] is not None:
            user.email = user_modifs['email']
        if user_modifs['name'] is not None:
            user.name = user_modifs['name']

        user.put()
        self.response.write(json.encode(entity_to_dict(user)))

    @treat_empty_string_as_none('key')
    @fallback_param_to_req('key')
    @returns_json
    def delete(self, key=None):
        if key is None:
            user_not_found()

        user = get_one_user(self, key)
        user.key.delete()
        res = {'message': 'User successfully deleted.'}
        self.response.write(json.encode(res))
