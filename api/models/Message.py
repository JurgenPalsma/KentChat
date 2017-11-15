from google.appengine.ext import ndb

from .Conversation import Conversation
from .utils import SerializableModel

class Message(SerializableModel, ndb.Model):
    conversation = ndb.KeyProperty(Conversation, required=True)
    post_time = ndb.DateTimeProperty(required=True)
    content = ndb.StringProperty(required=True)
