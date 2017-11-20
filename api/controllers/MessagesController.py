import sys
sys.path.append('..')

from google.appengine.ext import ndb
import webapp2
from webapp2_extras import json

from models import Message
from utils import returns_json, fallback_param_to_req, get_params_from_request, treat_empty_string_as_none, request_post_require

from UsersController import user_not_found, get_one_user
from ConversationsController import get_one_conversation, conversation_not_found

def message_not_found(self):
    self.abort(404)

def get_one_message(self, msg_id):
    try:
        message = ndb.Key(urlsafe=msg_id).get()
        if message is None:
            message_not_found(self)
        else:
            return message
    except ValueError as e:
        message_not_found(self)

class MessagesController(webapp2.RequestHandler):

    @treat_empty_string_as_none('conv_id', 'msg_id')
    @fallback_param_to_req('conv_id', 'msg_id')
    @returns_json
    def get(self, conv_id=None, msg_id=None):
        print('GET on /conversations/{}/messages/{}'.format(conv_id, msg_id))

        if msg_id is None: # Return the list of messages
            conversation = get_one_conversation(self, conv_id)
            res = [msg.to_dict() for msg in Message.query(ancestor=conversation.key).order(Message.post_time)]
        else: # Return one message
            message = get_one_message(self, msg_id)
            res = message.to_dict()

        self.response.write(json.encode(res))

    @treat_empty_string_as_none('conv_id')
    @fallback_param_to_req('conv_id')
    @request_post_require('content', 'user')
    @returns_json
    def post(self, conv_id=None):
        conversation = get_one_conversation(self, conv_id)

        message = Message(parent=conversation.key)
        message.content = self.request.get('content')
        message.user = get_one_user(self, self.request.get('user')).key

        print('POST on /messages: {}'.format(message))

        message.put()
        self.response.write(json.encode(message.to_dict()))

    @treat_empty_string_as_none('msg_id')
    @fallback_param_to_req('msg_id')
    @returns_json
    def put(self, conv_id=None, msg_id=None):
        message = get_one_message(self, msg_id)

        # edit message
        message_modifs = get_params_from_request(self, 'content')

        if message_modifs['content'] is not None:
            message.content = message_modifs['content']

        message.put()
        self.response.write(json.encode(message.to_dict()))

    @treat_empty_string_as_none('msg_id')
    @fallback_param_to_req('msg_id')
    @returns_json
    def delete(self, msg_id=None):
        if msg_id is None:
            message_not_found()

        message = get_one_message(self, msg_id)
        message.key.delete()
        res = {'message': 'Message successfully deleted.'}
        self.response.write(json.encode(res))
