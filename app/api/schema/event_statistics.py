from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Schema
from sqlalchemy import distinct, func

from app.api.helpers.cache import cache
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
    sessions_withdrawn = fields.Method("sessions_withdrawn_count")
    sessions_canceled = fields.Method("sessions_canceled_count")
    speakers = fields.Method("speakers_count")
    sessions = fields.Method("sessions_count")
    sponsors = fields.Method("sponsors_count")
    speaker_without_session = fields.Method("speaker_without_session_count")

    @cache.memoize(50)
    def get_session_stats(self, event):
        stats = (
            Session.query.filter_by(event_id=event.id, deleted_at=None)
            .with_entities(Session.state, func.count())
            .group_by(Session.state)
            .all()
        )
        data = dict(stats)
        data['all'] = sum([x for _, x in stats])

        return data

    def sessions_draft_count(self, obj):
        return self.get_session_stats(obj).get('draft', 0)

    def sessions_submitted_count(self, obj):
        return self.get_session_stats(obj).get('all', 0)

    def sessions_accepted_count(self, obj):
        return self.get_session_stats(obj).get('accepted', 0)

    def sessions_confirmed_count(self, obj):
        return self.get_session_stats(obj).get('confirmed', 0)

    def sessions_pending_count(self, obj):
        return self.get_session_stats(obj).get('pending', 0)

    def sessions_rejected_count(self, obj):
        return self.get_session_stats(obj).get('rejected', 0)

    def sessions_withdrawn_count(self, obj):
        return self.get_session_stats(obj).get('withdrawn', 0)

    def sessions_canceled_count(self, obj):
        return self.get_session_stats(obj).get('canceled', 0)

    def get_speaker_stats(self, event):
        stats = (
            Speaker.query.join(Speaker.sessions)
            .filter(
                Speaker.event_id == event.id,
                Speaker.deleted_at == None,
                Session.deleted_at == None,
            )
            .with_entities(Session.state, func.count(distinct(Speaker.id)))
            .group_by(Session.state)
            .all()
        )
        data = dict(stats)
        data['total'] = sum([x for _, x in stats])

        return data

    def speaker_without_session_count(self, obj):
        return Speaker.query.filter(
            Speaker.sessions == None,
            Speaker.event_id == obj.id,
            Speaker.deleted_at == None,
        ).count()

    @cache.memoize(50)
    def speakers_count(self, obj):
        stats = self.get_speaker_stats(obj)
        serial_data = {
            'accepted': 0,
            'confirmed': 0,
            'pending': 0,
            'rejected': 0,
            'withdrawn': 0,
            'canceled': 0,
            'total': 0,
            **stats,
        }
        return serial_data

    @cache.memoize(50)
    def sessions_count(self, obj):
        return Session.query.filter_by(event_id=obj.id, deleted_at=None).count()

    @cache.memoize(50)
    def sponsors_count(self, obj):
        return Sponsor.query.filter_by(event_id=obj.id, deleted_at=None).count()
