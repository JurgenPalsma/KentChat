import sys
if '..' not in sys.path:
    sys.path.append('..')

from google.appengine.ext import ndb
import webapp2
from webapp2_extras import json

from models import Conversation
from utils import returns_json, fallback_param_to_req, get_params_from_request, treat_empty_string_as_none

from UsersController import user_not_found, get_one_user

def conversation_not_found(self):
    self.abort(404)

def get_one_conversation(self, conv_id):
    try:
        conversation = ndb.Key(urlsafe=conv_id).get()
        if conversation is None:
            conversation_not_found(self)
        else:
            return conversation
    except ValueError as e:
        conversation_not_found(self)

class ConversationsController(webapp2.RequestHandler):

    @treat_empty_string_as_none('conv_id')
    @fallback_param_to_req('conv_id')
    @returns_json
    def get(self, conv_id=None):
        print('GET on /conversations/{}'.format(conv_id))
        if conv_id is None: # Return the list of conversations
            res = [conv.to_dict() for conv in Conversation.query()]
        else: # Return one conversation
            conversation = get_one_conversation(self, conv_id)
            res = conversation.to_dict()

        self.response.write(json.encode(res))

    @returns_json
    def post(self):
        try:
            users_ids = json.decode(unicode(self.request.get('users_ids', default_value=None)))
            if users_ids is None or len(users_ids) is 0:
                user_not_found(self, user_id=users_ids)
        except (ValueError, UnicodeError) as e:
            user_not_found(self, user_id=e)

        conversation = Conversation()
        conversation.users = [get_one_user(self, user_id).key for user_id in users_ids]
        if self.request.get('name', default_value=None) is not None:
            conversation.name = self.request.get('name', default_value=None)

        print('POST on /conversations: {}'.format(conversation))

        conversation.put()
        self.response.write(json.encode(conversation.to_dict()))

    @treat_empty_string_as_none('conv_id')
    @fallback_param_to_req('conv_id')
    @returns_json
    def put(self, conv_id=None):
        # Retrieve conversation
        if conv_id is None:
            return conversation_not_found(self)
        else:
            conversation = get_one_conversation(self, conv_id)

        # edit conversation
        conversation_modifs = get_params_from_request(self, 'users', 'name')

        if conversation_modifs['users'] is not None:
            try:
                users_ids = json.decode(unicode(conversation_modifs['users']))
                if users_ids is None or len(users_ids) is 0:
                    user_not_found(self, user_id=users_ids)

                conversation.users = [get_one_user(self, user_id).key for user_id in users_ids]
            except (ValueError, UnicodeError) as e:
                user_not_found(self, user_id=e)


        if conversation_modifs['name'] is not None:
            conversation.name = conversation_modifs['name']


        conversation.put()
        self.response.write(json.encode(conversation.to_dict()))

    @treat_empty_string_as_none('conv_id')
    @fallback_param_to_req('conv_id')
    @returns_json
    def delete(self, conv_id=None):
        if conv_id is None:
            conversation_not_found()

        conversation = get_one_conversation(self, conv_id)
        conversation.key.delete()
        res = {'message': 'Conversation successfully deleted.'}
        self.response.write(json.encode(res))
