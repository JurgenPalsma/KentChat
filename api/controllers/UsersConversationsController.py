import sys
if '..' not in sys.path:
    sys.path.append('..')

from google.appengine.ext import ndb
import webapp2
from webapp2_extras import json

from models import Conversation
from utils import returns_json, fallback_param_to_req, treat_empty_string_as_none

from UsersController import user_not_found, get_one_user

class UsersConversationsController(webapp2.RequestHandler):

    @treat_empty_string_as_none('user_id')
    @fallback_param_to_req('user_id')
    @returns_json
    def get(self, user_id=None):
        print('GET on /users/{}/conversations'.format(user_id))
        if user_id is None: # Return the list of users
            user_not_found

        user = get_one_user(self, user_id).key

        conversations = Conversation.query().filter(Conversation.users.IN([user]))
        res = [conv.to_dict() for conv in conversations]

        self.response.write(json.encode(res))
