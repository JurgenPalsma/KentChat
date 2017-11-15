from google.appengine.ext import ndb

class User(ndb.Model):
    # identity = ndb.KeyProperty(kind='string', required=True)
    email = ndb.StringProperty(required=True)
    name = ndb.StringProperty(required=True)
