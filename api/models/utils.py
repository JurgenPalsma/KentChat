from webapp2_extras import json
from google.appengine.ext import ndb

# A model witch can be easily converted to a python dictionary
class SerializableModel(ndb.Model):
    def _to_dict(self, *args, **kwargs):
        print(self)
        result = super(SerializableModel, self)._to_dict(*args, **kwargs)
        if self.key:
            result['key'] = self.key.urlsafe()
        return result
    to_dict = _to_dict

    def to_json(self):
        dicted = self.to_dict()
        return json.encode(dicted)
