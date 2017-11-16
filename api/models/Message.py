from google.appengine.ext import ndb

from .Conversation import Conversation
from .utils import SerializableModel

from datetime import datetime

class Message(SerializableModel, ndb.Model):
    # conversation = ndb.KeyProperty(Conversation, required=True)
    post_time = ndb.DateTimeProperty(required=True, auto_now_add=True)
    content = ndb.StringProperty(required=True)

    def _to_dict(self, *args, **kwargs):
        res = super(Message, self)._to_dict(*args, **kwargs)
        # converts datetime to utc timestamp
        res['post_time'] = (res['post_time'] - datetime.utcfromtimestamp(0)).total_seconds()
        return res
    to_dict = _to_dict
