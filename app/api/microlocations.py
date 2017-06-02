from app.api.helpers.permissions import jwt_required
from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from marshmallow_jsonapi.flask import Schema, Relationship
from marshmallow_jsonapi import fields
from app.models import db
from app.models.microlocation import Microlocation


class MicrolocationSchema(Schema):
    """
    Api schema for Microlocation Model
    """
    class Meta:
        """
        Meta class for Microlocation Api Schema
        """
        type_ = 'microlocation'
        self_view = 'v1.microlocation_detail'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'v1.session_list'

    id = fields.Str(dump_only=True)
    name = fields.Str(required=True)
    latitude = fields.Float()
    longitude = fields.Float()
    floor =  fields.Integer()
    room = fields.Str()
    session = Relationship(attribute='session',
                           self_view='v1.microlocation_session',
                           self_view_kwargs={'id': '<id>'},
                           related_view='v1.session_detail',
                           related_view_kwargs={'microlocation_id': '<id>'},
                           schema='SessionSchema',
                           type_='session')
    event = Relationship(attribute='event',
                         self_view='v1.microlocation_event',
                         self_view_kwargs={'id': '<id>'},
                         related_view='v1.event_detail',
                         related_view_kwargs={'microlocation_id': '<id>'},
                         schema='EventSchema',
                         type_='event')


class MicrolocationDetail(ResourceDetail):
    """
    Microlocation detail by id
    """
    decorators = (jwt_required, )
    schema = MicrolocationSchema
    data_layer = {'session': db.session,
                  'model': Microlocation}


class MicrolocationList(ResourceList):
    """
    List and create Microlocations
    """
    def query(self, view_kwargs):
        query_ = self.session.query(Microlocation)
        if view_kwargs.get('id') is not None:
            query_ = query_.join(Event).filter(Event.id == view_kwargs['id'])
        return query_

    def before_create_object(self, data, view_kwargs):
        if view_kwargs.get('id') is not None:
            event = self.session.query(Event).filter_by(id=view_kwargs['id']).one()
            data['event_id'] = event.id

    decorators = (jwt_required, )
    schema = MicrolocationSchema
    data_layer = {'session': db.session,
                  'model': Microlocation,
                  'methods': {
                      'query': query,
                      'before_create_object': before_create_object
                  }}


class MicrolocationRelationship(ResourceRelationship):
    """
    Microlocation Relationship
    """
    decorators = (jwt_required, )
    schema = MicrolocationSchema
    data_layer = {'session': db.session,
                  'model': Microlocation}


