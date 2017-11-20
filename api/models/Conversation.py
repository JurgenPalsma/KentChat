from google.appengine.ext import ndb

from .User import User
from .utils import SerializableModel

class Conversation(SerializableModel, ndb.Model):
    users = ndb.KeyProperty(User, repeated=True)
    name = ndb.StringProperty(required=False)

    def _to_dict(self, *args, **kwargs):
        res = super(Conversation, self)._to_dict(*args, **kwargs)
        res['users'] = [user.urlsafe() for user in res['users']]
        return res
    to_dict = _to_dict
