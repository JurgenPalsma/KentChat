import sys
if '..' not in sys.path:
    sys.path.append('..')

from google.appengine.ext import ndb
import webapp2
from webapp2_extras import json

from models import User, Conversation
from utils import returns_json, fallback_param_to_req, get_params_from_request, treat_empty_string_as_none, request_post_require

from AuthController import auth_error

def user_not_found(self, user_id=None, *args, **kwargs):
    if user_id is not None:
        self.abort(404, 'User not found: {}'.format(user_id), *args, **kwargs)
    else:
        self.abort(404, *args, **kwargs)

# Get one conversation.
# If the auth token is provided, checks if the user corresponds to the auth_token
def get_one_user(self, user_id, auth_token=None):
    print('getting user {}'.format(user_id))
    try:
        user = ndb.Key(urlsafe=user_id).get()
        if user is None:
            user_not_found(self, user_id=user_id)
        else:
            if auth_token is not None: # If auth token has been given, check that it is the correct user. Else, we don't care
                if user.token != auth_token:
                    auth_error(self)
                else:
                     return user
            else:
                return user
    except Exception as e:
        user_not_found(self, user_id=user_id)

class NonFriendsController(webapp2.RequestHandler):

    @treat_empty_string_as_none('user_id')
    @fallback_param_to_req('user_id')
    @returns_json
    def get(self, user_id=None):
        print('GET on /users/{}/nonfriends'.format(user_id))
        if user_id is None: # Return the list of users
            user_not_found(self, user_id=user_id)
        else: # Return one user
            user = get_one_user(self, user_id)
            conversations = Conversation.query().filter(Conversation.users.IN([user.key]))
            friends = reduce(lambda a, b: a + b, [conv.users for conv in conversations], [])

            all_users = [user.key for user in User.query()]

            non_friends = [user.get().to_dict() for user in list(set(all_users) - set(friends))]

            self.response.write(json.encode(non_friends))
