import sys
if '..' not in sys.path:
    sys.path.append('..')

from google.appengine.ext import ndb
import webapp2
from webapp2_extras import json

from models import Message, User
from utils import returns_json, fallback_param_to_req, get_params_from_request, treat_empty_string_as_none, request_post_require

from UsersController import user_not_found, get_one_user
from ConversationsController import get_one_conversation, conversation_not_found
from AuthController import require_auth_token, auth_error

def message_not_found(self, msg_id=None, *args, **kwargs):
    if msg_id is not None:
        self.abort(404, 'Message not found: {}'.format(msg_id), *args, **kwargs)
    else:
        self.abort(404, *args, **kwargs)


def get_one_message(self, msg_id, auth_token=None):
    try:
        message = ndb.Key(urlsafe=msg_id).get()
        if message is None:
            message_not_found(self, msg_id=msg_id)
        else:
            if auth_token is not None:
                user = User.get_by_auth_token(auth_token)
                if user.key == message.user:
                    return message
                else:
                    auth_error(self, 'This message is not accessible to this user')
            else:
                return message

    except ValueError as e:
        message_not_found(self, 'Unknown error: {}'.format(e))

class MessagesController(webapp2.RequestHandler):

    @require_auth_token
    @treat_empty_string_as_none('conv_id', 'msg_id')
    @fallback_param_to_req('conv_id', 'msg_id')
    @returns_json
    def get(self, conv_id=None, msg_id=None, auth_token=None):
        print('GET on /conversations/{}/messages/{}'.format(conv_id, msg_id))

        if msg_id is None: # Return the list of messages
            conversation = get_one_conversation(self, conv_id, auth_token=auth_token)
            res = [msg.to_dict() for msg in Message.query(ancestor=conversation.key).order(Message.post_time)]
        else: # Return one message
            message = get_one_message(self, msg_id)
            res = message.to_dict()

        self.response.write(json.encode(res))

    @require_auth_token
    @treat_empty_string_as_none('conv_id')
    @fallback_param_to_req('conv_id')
    @request_post_require('content')
    @returns_json
    def post(self, conv_id=None, auth_token=None):
        conversation = get_one_conversation(self, conv_id, auth_token=auth_token)
        user = User.get_by_auth_token(auth_token)

        message = Message(parent=conversation.key)
        message.content = self.request.get('content')
        message.user = user.key

        print('POST on /messages: {}'.format(message))

        message.put()
        self.response.write(json.encode(message.to_dict()))

    @require_auth_token
    @treat_empty_string_as_none('msg_id')
    @fallback_param_to_req('msg_id')
    @returns_json
    def put(self, conv_id=None, msg_id=None, auth_token=None):
        message = get_one_message(self, msg_id, auth_token=auth_token)

        # edit message
        message_modifs = get_params_from_request(self, 'content')

        if message_modifs['content'] is not None:
            message.content = message_modifs['content']

        message.put()
        self.response.write(json.encode(message.to_dict()))

    @require_auth_token
    @treat_empty_string_as_none('msg_id')
    @fallback_param_to_req('msg_id')
    @returns_json
    def delete(self, msg_id=None, auth_token=None):
        if msg_id is None:
            message_not_found(self, msg_id=msg_id)

        message = get_one_message(self, msg_id, auth_token=auth_token)
        message.key.delete()
        res = {'message': 'Message successfully deleted.'}
        self.response.write(json.encode(res))
