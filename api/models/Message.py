from google.appengine.ext import ndb

from .User import User

class Message(ndb.Model):
    uuid = ndb.KeyProperty(kind='str', required=True)
    post_time = ndb.DateTimeProperty(required=True)
    user_from = ndb.StructuredProperty(User, required=True)
    user_to = ndb.StructuredProperty(User, required=True)
