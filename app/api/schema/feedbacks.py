"""Schema class for Feedbacks"""

from marshmallow.validate import Range
from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Relationship

from app.api.helpers.utilities import dasherize
from app.api.schema.base import SoftDeletionSchema


class FeedbackSchema(SoftDeletionSchema):
    """
    Api schema for Feedback Model
    """

    class Meta:
        """
        Meta class for Feedback Api Schema
        """

        type_ = 'feedback'
        self_view = 'v1.feedback_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    id = fields.Str(dump_only=True)
    rating = fields.Float(required=True, validate=Range(min=1, max=5))
    comment = fields.Str(required=False)
    event = Relationship(
        self_view='v1.feedback_event',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.event_detail',
        related_view_kwargs={'feedback_id': '<id>'},
        schema='EventSchemaPublic',
        type_='event',
    )
    session = Relationship(
        self_view='v1.feedback_session',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.session_detail',
        related_view_kwargs={'feedback_id': '<id>'},
        schema='SessionSchema',
        type_='session',
    )
    user = Relationship(
        self_view='v1.feedback_user',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.user_detail',
        related_view_kwargs={'feedback_id': '<id>'},
        schema='UserSchema',
        type_='user',
    )
