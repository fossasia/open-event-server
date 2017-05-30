from datetime import datetime
from app.api.helpers.jwt import jwt_required
from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from marshmallow_jsonapi.flask import Schema, Relationship
from marshmallow_jsonapi import fields
from app.models import db
from app.models.event import Event


class EventSchema(Schema):

    class Meta:
        type_ = 'event'
        self_view = 'v1.event_detail'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'v1.event_list'

    id = fields.Str(dump_only=True)
    identifier = fields.Str(dump_only=True)
    name = fields.Str()
    event_url = fields.Str()
    ticket = Relationship(attribute='ticket',
                          self_view='v1.event_ticket',
                          self_view_kwargs={'id': '<id>'},
                          related_view='v1.ticket_detail',
                          related_view_kwargs={'id': '<id>'},
                          schema='TicketSchema',
                          many=True,
                          type_='ticket')


class EventList(ResourceList):
    decorators = (jwt_required, )
    schema = EventSchema
    data_layer = {'session': db.session,
                  'model': Event}


class EventRelationship(ResourceRelationship):
    decorators = (jwt_required, )
    schema = EventSchema
    data_layer = {'session': db.session,
                  'model': Event}


class EventDetail(ResourceDetail):

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
    schema = EventSchema
    data_layer = {'session': db.session,
                  'model': Event}
