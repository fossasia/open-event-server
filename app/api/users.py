from datetime import datetime
from app.api.helpers.jwt import jwt_required
from flask_rest_jsonapi import ResourceDetail, ResourceList
from marshmallow_jsonapi.flask import Schema, Relationship
from marshmallow_jsonapi import fields
from app.models import db
from app.models.user import User


class UserSchema(Schema):
    class Meta:
        type_ = 'user'
        self_view = 'v1.user_detail'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'v1.user_list'

    id = fields.Str(dump_only=True)
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True)
    avatar = fields.Str()
    is_super_admin = fields.Boolean()
    is_admin = fields.Boolean()
    is_verified = fields.Boolean()
    signup_at = fields.DateTime()
    last_accessed_at = fields.DateTime()
    created_at = fields.DateTime()
    deleted_at = fields.DateTime()
    firstname = fields.Str()
    lastname = fields.Str()
    details = fields.Str()
    contact = fields.Str()
    facebook = fields.Str()
    twitter = fields.Str()
    instagram = fields.Str()
    google = fields.Str()
    avatar_uploaded = fields.Str()
    thumbnail = fields.Str()
    small = fields.Str()
    icon = fields.Str()


class UserList(ResourceList):
    decorators = (jwt_required, )
    schema = UserSchema
    data_layer = {'session': db.session,
                  'model': User}


class UserDetail(ResourceDetail):
    def delete(self, *args, **kwargs):
        """
        Function for soft-delete
        :param args:
        :param kwargs:
        :return:
        """
        obj = self._data_layer.get_object(kwargs)
        obj.deleted_at = datetime.now()
        return {'meta': {'message': 'Object successfully deleted'}}

    decorators = (jwt_required, )
    schema = UserSchema
    data_layer = {'session': db.session,
                  'model': User}


