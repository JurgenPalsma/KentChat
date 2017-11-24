from google.appengine.ext import ndb

from .utils import SerializableModel

class User(SerializableModel, ndb.Model):
    # identity = ndb.KeyProperty(kind='string', required=True)
    email = ndb.StringProperty(required=True)
    name = ndb.StringProperty(required=True)
    password = ndb.StringProperty(required=True)
    token = ndb.StringProperty(required=True)

    def _to_dict(self, *args, **kwargs):
        res = super(User, self)._to_dict(*args, **kwargs)
        # Secret stuff
        res.pop('token', None)
        res.pop('password', None)
        return res
    to_dict = _to_dict

    @staticmethod
    def get_by_auth_token(auth_token):
        return User.query(User.token == auth_token).get()
