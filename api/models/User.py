from google.appengine.ext import ndb

from .utils import SerializableModel

class User(SerializableModel, ndb.Model):
    # identity = ndb.KeyProperty(kind='string', required=True)
    email = ndb.StringProperty(required=True)
    name = ndb.StringProperty(required=True)
