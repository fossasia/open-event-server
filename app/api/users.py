from datetime import datetime
from flask_rest_jsonapi import ResourceDetail, ResourceList
from marshmallow_jsonapi.flask import Schema, Relationship
from marshmallow_jsonapi import fields
from app.models import db
from app.models.user import User
from app.api.helpers.permissions import is_admin, is_user_itself


class UserSchema(Schema):
    """
    Api schema for User Model
    """
    class Meta:
        """
        Meta class for User Api Schema
        """
        type_ = 'user'
        self_view = 'v1.user_detail'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'v1.user_list'

    id = fields.Str(dump_only=True)
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True)
    avatar = fields.Str()
    is_super_admin = fields.Boolean(dump_only=True)
    is_admin = fields.Boolean(dump_only=True)
    is_verified = fields.Boolean(dump_only=True)
    signup_at = fields.DateTime(dump_only=True)
    last_accessed_at = fields.DateTime(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    deleted_at = fields.DateTime(dump_only=True)
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
    """
    List and create Users
    """
    get = is_admin(ResourceList.get.__func__)
    schema = UserSchema
    data_layer = {'session': db.session,
                  'model': User}


class UserDetail(ResourceDetail):
    """
    User detail by id
    """
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

    decorators = (is_user_itself, )
    schema = UserSchema
    data_layer = {'session': db.session,
                  'model': User}


