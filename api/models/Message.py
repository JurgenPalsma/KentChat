from google.appengine.ext import ndb

from .User import User
from .utils import SerializableModel

from datetime import datetime

class Message(SerializableModel, ndb.Model):
    user = ndb.KeyProperty(User, required=True)
    post_time = ndb.DateTimeProperty(required=True, auto_now_add=True)
    content = ndb.StringProperty(required=True)

    def _to_dict(self, *args, **kwargs):
        res = super(Message, self)._to_dict(*args, **kwargs)
        # converts datetime to utc timestamp
        res['post_time'] = (res['post_time'] - datetime.utcfromtimestamp(0)).total_seconds()
        res['user'] = res['user'].urlsafe()
        return res
    to_dict = _to_dict
