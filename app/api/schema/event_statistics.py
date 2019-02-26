from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Schema

from app.api.helpers.utilities import dasherize
from app.models.session import Session
from app.models.speaker import Speaker
from app.models.sponsor import Sponsor


class EventStatisticsGeneralSchema(Schema):
    """
    Api schema for general statistics of event
    """
    class Meta:
        """
        Meta class
        """
        type_ = 'event-statistics-general'
        self_view = 'v1.event_statistics_general_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    id = fields.Str()
    identifier = fields.Str()
    sessions_draft = fields.Method("sessions_draft_count")
    sessions_submitted = fields.Method("sessions_submitted_count")
    sessions_accepted = fields.Method("sessions_accepted_count")
    sessions_confirmed = fields.Method("sessions_confirmed_count")
    sessions_pending = fields.Method("sessions_pending_count")
    sessions_rejected = fields.Method("sessions_rejected_count")
    speakers = fields.Method("speakers_count")
    speakers_accepted = fields.Method("speakers_accepted_count")
    speakers_confirmed = fields.Method("speakers_confirmed_count")
    speakers_pending = fields.Method("speakers_pending_count")
    speakers_rejected = fields.Method("speakers_rejected_count")
    sessions = fields.Method("sessions_count")
    sponsors = fields.Method("sponsors_count")

    def sessions_draft_count(self, obj):
        return Session.query.filter_by(event_id=obj.id, state='draft').count()

    def sessions_submitted_count(self, obj):
        return Session.query.filter_by(event_id=obj.id, state='submitted').count()

    def sessions_accepted_count(self, obj):
        return Session.query.filter_by(event_id=obj.id, state='accepted').count()

    def speakers_accepted_count(self, obj):
        current_query = Session.query.filter_by(event_id=obj.id, state='accepted')
        all_speakers = []
        for sessions in current_query:
            all_speakers += [speaker for speaker in sessions.speakers]
        return len(set(all_speakers))

    def speakers_confirmed_count(self, obj):
        current_query = Session.query.filter_by(event_id=obj.id, state='confirmed')
        all_speakers = []
        for sessions in current_query:
            all_speakers += [speaker for speaker in sessions.speakers]
        return len(set(all_speakers))

    def speakers_pending_count(self, obj):
        current_query = Session.query.filter_by(event_id=obj.id, state='pending')
        all_speakers = []
        for sessions in current_query:
            all_speakers += [speaker for speaker in sessions.speakers]
        return len(set(all_speakers))

    def speakers_rejected_count(self, obj):
        current_query = Session.query.filter_by(event_id=obj.id, state='rejected')
        all_speakers = []
        for sessions in current_query:
            all_speakers += [speaker for speaker in sessions.speakers]
        return len(set(all_speakers))

    def sessions_confirmed_count(self, obj):
        return Session.query.filter_by(event_id=obj.id, state='confirmed').count()

    def sessions_pending_count(self, obj):
        return Session.query.filter_by(event_id=obj.id, state='pending').count()

    def sessions_rejected_count(self, obj):
        return Session.query.filter_by(event_id=obj.id, state='rejected').count()

    def speakers_count(self, obj):
        return Speaker.query.filter_by(event_id=obj.id).count()

    def sessions_count(self, obj):
        return Session.query.filter_by(event_id=obj.id).count()

    def sponsors_count(self, obj):
        return Sponsor.query.filter_by(event_id=obj.id).count()
