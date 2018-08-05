from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Relationship

from app.api.helpers.utilities import dasherize
from utils.common import use_defaults
from app.api.schema.base import SoftDeletionSchema


@use_defaults()
class UserFavouriteEventSchema(SoftDeletionSchema):
    """
    Api schema for User Favourite Event Model
    """

    class Meta:
        """
        Meta class for User Favourite Event Api Schema
        """
        type_ = 'user-favourite-event'
        self_view = 'v1.user_favourite_event_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    id = fields.Str(dump_only=True)
    event = Relationship(attribute='event',
                         self_view='v1.user_favourite_event_event',
                         self_view_kwargs={'id': '<id>'},
                         related_view='v1.event_detail',
                         related_view_kwargs={'user_favourite_event_id': '<id>'},
                         schema='EventSchemaPublic',
                         type_='event')
    user = Relationship(attribute='user',
                        self_view='v1.user_favourite_event_user',
                        self_view_kwargs={'id': '<id>'},
                        related_view='v1.user_detail',
                        related_view_kwargs={'user_favourite_event_id': '<id>'},
                        schema='UserSchema',
                        type_='user')
