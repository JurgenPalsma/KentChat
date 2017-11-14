from google.appengine.ext import ndb

class User(ndb.Model):
    """Sub model for representing an author."""
    uuid = ndb.StringProperty(indexed=False)
    email = ndb.StringProperty(indexed=False)
