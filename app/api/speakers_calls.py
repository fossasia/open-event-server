from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from flask_rest_jsonapi.exceptions import ObjectNotFound
from sqlalchemy.orm.exc import NoResultFound

from app.api.bootstrap import api
from app.api.helpers.exceptions import ForbiddenException, ConflictException
from app.api.helpers.permission_manager import has_access
from app.api.helpers.utilities import require_relationship
from app.api.schema.speakers_calls import SpeakersCallSchema
from app.models import db
from app.models.event import Event
from app.models.speakers_call import SpeakersCall


class SpeakersCallList(ResourceList):
    """
    create Speakers Call
    """
    def before_post(self, args, kwargs, data):
        """
        before post method to check for required relationship and proper permission
        :param args:
        :param kwargs:
        :param data:
        :return:
        """
        require_relationship(['event'], data)
        if not has_access('is_coorganizer', event_id=data['event']):
            raise ForbiddenException({'source': ''}, 'Co-organizer access is required.')

    def before_create_object(self, data, view_kwargs):
        """
        method to check if speaker calls object already exists for an event
        :param data:
        :param view_kwargs:
        :return:
        """
        try:
            speakers_call = self.session.query(SpeakersCall).filter_by(event_id=data['event'], deleted_at=None).one()
            event = speakers_call.event
            if speakers_call.starts_at > event.starts_at or speakers_call.ends_at > event.starts_at:
                raise ForbiddenException({'source': ''}, "Speakers call date can\'t be after the event start date")
        except NoResultFound:
            pass
        else:
            raise ConflictException({'pointer': '/data/relationships/event'},
                                    "Speakers Call already exists for this event")

    schema = SpeakersCallSchema
    methods = ['POST', ]
    data_layer = {'session': db.session,
                  'model': SpeakersCall,
                  'methods': {
                      'before_create_object': before_create_object
                  }}


class SpeakersCallDetail(ResourceDetail):
    """
     speakers call detail by id
    """
    def before_patch(self, args, kwargs, data):
        """
        before patch method to check for existing speakers-call
        :param args:
        :param kwargs:
        :param data:
        :return:
        """
        if kwargs.get('event_id'):
            try:
                speakers_call = SpeakersCall.query.filter_by(event_id=kwargs['event_id']).one()
                event = speakers_call.event
                if speakers_call.starts_at > event.starts_at or speakers_call.ends_at > event.starts_at:
                    raise ForbiddenException({'source': ''}, "Speakers call date can\'t be after the event start date")
            except NoResultFound:
                raise ObjectNotFound({'source': ''}, "Object: not found")
            kwargs['id'] = speakers_call.id


    def before_get_object(self, view_kwargs):
        """
        before get method to get the resource id for fetching details
        :param view_kwargs:
        :return:
        """
        if view_kwargs.get('event_identifier'):
            try:
                event = self.session.query(Event).filter_by(identifier=view_kwargs['event_identifier']).one()
            except NoResultFound:
                raise ObjectNotFound({'parameter': 'event_identifier'},
                                     "Event: {} not found".format(view_kwargs['event_identifier']))
            else:
                view_kwargs['event_id'] = event.id

        if view_kwargs.get('event_id'):
            try:
                speakers_call = self.session.query(SpeakersCall).filter_by(event_id=view_kwargs['event_id']).one()
            except NoResultFound:
                raise ObjectNotFound({'parameter': 'event_identifier'}, "Object: not found")
            view_kwargs['id'] = speakers_call.id

    decorators = (api.has_permission('is_coorganizer', fetch="event_id", fetch_as="event_id",
                                     model=SpeakersCall, methods="PATCH,DELETE"),)
    schema = SpeakersCallSchema
    data_layer = {'session': db.session,
                  'model': SpeakersCall,
                  'methods': {
                      'before_get_object': before_get_object
                  }}


class SpeakersCallRelationship(ResourceRelationship):
    """
    speakers call Relationship
    """
    decorators = (api.has_permission('is_coorganizer', fetch="event_id", fetch_as="event_id",
                                     model=SpeakersCall, methods="PATCH,DELETE"),)
    schema = SpeakersCallSchema
    methods = ['GET', 'PATCH']
    data_layer = {'session': db.session,
                  'model': SpeakersCall}
