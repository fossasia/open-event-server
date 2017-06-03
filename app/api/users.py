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
    order = Relationship(attribute='order',
                       self_view='v1.user_order',
                       self_view_kwargs={'id': '<id>'},
                       related_view='v1.order_list',
                       related_view_kwargs={'id': '<id>'},
                       schema='OrderSchema',
                       many=True,
                       type_='order')


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
    def before_get_object(self, view_kwargs):
        if view_kwargs.get('order_id') is not None:
            try:
                order = self.session.query(Order).filter_by(id=view_kwargs['order_id']).one()
            except NoResultFound:
                raise ObjectNotFound({'parameter': 'order_id'},
                                     "Order: {} not found".format(view_kwargs['order_id']))
            else:
                if order.user_id is not None:
                    view_kwargs['id'] = order.user_id
                else:
                    view_kwargs['id'] = None

    decorators = (is_user_itself, )
    schema = UserSchema
    data_layer = {'session': db.session,
                  'model': User}


