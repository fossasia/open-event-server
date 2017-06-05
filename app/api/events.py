from app.api.helpers.permissions import jwt_required
from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from marshmallow_jsonapi.flask import Schema, Relationship
from marshmallow_jsonapi import fields
from sqlalchemy.orm.exc import NoResultFound
from flask_rest_jsonapi.exceptions import ObjectNotFound
from app.models import db
from app.models.event import Event
from app.models.sponsor import Sponsor
from app.models.track import Track
from app.models.session_type import SessionType


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
                          related_view_kwargs={'event_id': '<id>'},
                          schema='TicketSchema',
                          many=True,
                          type_='ticket')
    microlocation = Relationship(attribute='microlocation',
                                 self_view='v1.event_microlocation',
                                 self_view_kwargs={'id': '<id>'},
                                 related_view='v1.microlocation_detail',
                                 related_view_kwargs={'event_id': '<id>'},
                                 schema='MicrolocationSchema',
                                 many=True,
                                 type_='microlocation')
    social_link = Relationship(attribute='social_link',
                               self_view='v1.event_social_link',
                               self_view_kwargs={'id': '<id>'},
                               related_view='v1.social_link_detail',
                               related_view_kwargs={'event_id': '<id>'},
                               schema='SocialLinkSchema',
                               many=True,
                               type_='social_link')
    tracks = Relationship(attribute='track',
                          self_view='v1.event_tracks',
                          self_view_kwargs={'id': '<id>'},
                          related_view='v1.track_list',
                          related_view_kwargs={'event_id': '<id>'},
                          schema='TrackSchema',
                          many=True,
                          type_='track')
    sponsor = Relationship(attribute='sponsor',
                           self_view='v1.event_sponsor',
                           self_view_kwargs={'id': '<id>'},
                           related_view='v1.sponsor_list',
                           related_view_kwargs={'event_id': '<id>'},
                           schema='SponsorSchema',
                           many=True,
                           type_='sponsor')
    call_for_speaker = Relationship(attribute='call_for_paper',
                                    self_view='v1.event_call_for_paper',
                                    self_view_kwargs={'id': '<id>'},
                                    related_view='v1.call_for_paper_detail',
                                    related_view_kwargs={'event_id': '<id>'},
                                    schema='CallForPaperSchema',
                                    type_='sponsor')
    session_types = Relationship(attribute='session_type',
                                 self_view='v1.event_session_types',
                                 self_view_kwargs={'id': '<id>'},
                                 related_view='v1.session_type_list',
                                 related_view_kwargs={'event_id': '<id>'},
                                 schema='SessionTypeSchema',
                                 many=True,
                                 type_='session_type')


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

    def before_get_object(self, view_kwargs):
        if view_kwargs.get('sponsor_id') is not None:
            try:
                sponsor = self.session.query(Sponsor).filter_by(id=view_kwargs['sponsor_id']).one()
            except NoResultFound:
                raise ObjectNotFound({'parameter': 'sponsor_id'},
                                     "Sponsor: {} not found".format(view_kwargs['sponsor_id']))
            else:
                if sponsor.event_id is not None:
                    view_kwargs['id'] = sponsor.event_id
                else:
                    view_kwargs['id'] = None

        if view_kwargs.get('track_id') is not None:
            try:
                track = self.session.query(Track).filter_by(id=view_kwargs['track_id']).one()
            except NoResultFound:
                raise ObjectNotFound({'parameter': 'track_id'},
                                     "Track: {} not found".format(view_kwargs['track_id']))
            else:
                if track.event_id is not None:
                    view_kwargs['id'] = track.event_id
                else:
                    view_kwargs['id'] = None

        if view_kwargs.get('session_type_id') is not None:
            try:
                session_type = self.session.query(SessionType).filter_by(id=view_kwargs['session_type_id']).one()
            except NoResultFound:
                raise ObjectNotFound({'parameter': 'session_type_id'},
                                     "SessionType: {} not found".format(view_kwargs['session_type_id']))
            else:
                if session_type.event_id is not None:
                    view_kwargs['id'] = session_type.event_id
                else:
                    view_kwargs['id'] = None

    decorators = (jwt_required, )
    schema = EventSchema
    data_layer = {'session': db.session,
                  'model': Event,
                  'methods': {'before_get_object': before_get_object}}
