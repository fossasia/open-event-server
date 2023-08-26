from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship

from app.api.helpers.db import get_count, safe_query_kwargs
from app.api.helpers.errors import ConflictError
from app.api.helpers.utilities import require_relationship
from app.api.schema.tag import TagSchema
from app.models import db
from app.models.event import Event
from app.models.tag import Tag
from app.models.ticket_holder import TicketHolder


class TagList(ResourceList):
    """List User Emails for a user"""

    def query(self, view_kwargs):
        """
        query method for Notifications list
        :param view_kwargs:
        :return:
        """
        query_ = self.session.query(Tag)
        if view_kwargs.get('event_id'):
            event = safe_query_kwargs(Event, view_kwargs, 'event_id')
            query_ = (
                query_.join(Event).filter(Event.id == event.id).order_by(Tag.id.asc())
            )
        return query_

    view_kwargs = True
    methods = [
        "GET",
    ]
    schema = TagSchema
    data_layer = {'session': db.session, 'model': Tag, 'methods': {'query': query}}


class TagListPost(ResourceList):
    """Create new alternate email for a user"""

    @staticmethod
    def before_post(_args, _kwargs, data):
        """
        before post method to check for required relationship and proper permission
        :param args:
        :param kwargs:
        :param data:
        :return:
        """
        require_relationship(['event'], data)
        if (
            get_count(
                db.session.query(Tag.id).filter_by(
                    name=data.get('name'),
                    event_id=int(data['event']),
                    deleted_at=None,
                )
            )
            > 0
        ):
            raise ConflictError(
                {'pointer': '/data/attributes/name'}, "Name already exists"
            )

    schema = TagSchema
    methods = [
        'POST',
    ]
    data_layer = {
        'session': db.session,
        'model': Tag,
        'methods': {'before_post': before_post},
    }


class TagDetail(ResourceDetail):
    """User Email detail by id"""

    @staticmethod
    def before_patch(_obj, _kwargs, data):
        """
        before patch method to check for required relationship and proper permission
        :param args:
        :param kwargs:
        :param data:
        :return:
        """
        require_relationship(['event'], data)
        tag = (
            db.session.query(Tag)
            .filter_by(
                name=data.get('name'), event_id=int(data['event']), deleted_at=None
            )
            .first()
        )
        if tag and tag.is_read_only and tag.name != data.get('name'):
            raise ConflictError(
                {'pointer': '/data/attributes/is_read_only'},
                "Cannot update read-only tag",
            )

    @staticmethod
    def before_delete(_obj, kwargs):
        """
        before delete method to check for required relationship and proper permission
        :param args:
        :param kwargs:
        :param data:
        :return:
        """
        ticketHolders = TicketHolder.query.filter_by(tag_id=kwargs['id']).all()
        for item in ticketHolders:
            item.tag_id = None
            db.session.add(item)

    schema = TagSchema
    data_layer = {
        'session': db.session,
        'model': Tag,
        'methods': {'before_delete': before_delete, before_patch: 'before_patch'},
    }


class TagRelationship(ResourceRelationship):
    """User Email Relationship"""

    schema = TagSchema
    data_layer = {'session': db.session, 'model': Tag}
