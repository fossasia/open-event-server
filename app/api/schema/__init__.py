# Monkey Patch Marshmallow JSONAPI
from marshmallow_jsonapi.flask import Relationship


def serialize(self, attr, obj, accessor=None):
    if self.include_resource_linkage or self.include_data:
        return super(Relationship, self).serialize(attr, obj, accessor)
    return self._serialize(None, attr, obj)


Relationship.serialize = serialize
