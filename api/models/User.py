from google.appengine.ext import ndb

from random import choice

from .utils import SerializableModel

def generate_token(size=16):
    alphabet = 'abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    return reduce(lambda a, b: str(a) + str(b), [choice(alphabet) for _ in range(size)])

class User(SerializableModel, ndb.Model):
    # identity = ndb.KeyProperty(kind='string', required=True)
    email = ndb.StringProperty(required=True)
    name = ndb.StringProperty(required=True)
    password = ndb.StringProperty(required=True)
    tokens = ndb.StringProperty(repeated=True)

    def _to_dict(self, *args, **kwargs):
        res = super(User, self)._to_dict(*args, **kwargs)
        # Secret stuff
        res.pop('tokens', None)
        res.pop('password', None)
        return res
    to_dict = _to_dict

    @staticmethod
    def get_by_auth_token(auth_token):
        return User.query().filter(User.tokens.IN([auth_token])).get()

    def add_new_token(self):
        auth_token = generate_token()
        self.tokens.append(auth_token)
        return auth_token

    def remove_token(self, auth_token):
        if auth_token in self.tokens:
            self.tokens.remove(auth_token)
            return True
        else:
            return False
