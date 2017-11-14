from google.appengine.ext import ndb

from .User import User

class Message(ndb.Model):
    """Sub model for representing an author."""
    uuid = ndb.StringProperty(indexed=False)
    post_time = ndb.TimeProperty(index=False)
    user_from = ndb.StructuredProperty(User)
    user_to = ndb.StructuredProperty(User)
