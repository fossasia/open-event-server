from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from marshmallow_jsonapi.flask import Schema, Relationship
from marshmallow_jsonapi import fields
from app.models import db
from app.api.helpers.permissions import jwt_required, is_admin, is_user_itself
from sqlalchemy.orm.exc import NoResultFound
from flask_rest_jsonapi.exceptions import ObjectNotFound
from app.models.page import Page


class PageSchema(Schema):
    """
    Api schema for page Model
    """
    class Meta:
        """
        Meta class for page Api Schema
        """
        type_ = 'page'
        self_view = 'v1.page_detail'
        self_view_kwargs = {'id': '<id>'}

    id = fields.Str(dump_only=True)
    name = fields.Str(required=True)
    title = fields.Str()
    url = fields.Str(required=True)
    description = fields.Str()
    place = fields.Str()
    language = fields.Str()
    index = fields.Integer(default=0)


class PageList(ResourceList):
    """
    List and create page
    """
    post = is_admin(ResourceList.post.__func__)
    schema = PageSchema
    data_layer = {'session': db.session,
                  'model': Page}


class PageDetail(ResourceDetail):
    """
    Page detail by id
    """
    patch = is_admin(ResourceDetail.patch.__func__)
    delete = is_admin(ResourceDetail.delete.__func__)
    schema = PageSchema
    data_layer = {'session': db.session,
                  'model': Page}
