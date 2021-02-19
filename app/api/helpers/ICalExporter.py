from app.api.helpers.calendar.ical import to_ical
from app.models.event import Event


class ICalExporter:
    @staticmethod
    def export(event_id, user_id):
        """Takes an event id and returns the event in iCal format"""

        event = Event.query.get(event_id)

        return to_ical(event, user_id, include_sessions=True)
