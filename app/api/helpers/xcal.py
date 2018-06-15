from xml.etree.ElementTree import Element, SubElement, tostring
from flask import url_for
from sqlalchemy import asc

from app.models.session import Session
from app.models.event import Event as Event


class XCalExporter:
    def __init__(self):
        pass

    @staticmethod
    def export(event_id):
        """Takes an event id and returns the event in xCal format"""

        event = Event.query.get(event_id)

        i_calendar_node = Element('iCalendar')
        i_calendar_node.set('xmlns:xCal', 'urn:ietf:params:xml:ns:xcal')
        v_calendar_node = SubElement(i_calendar_node, 'vcalendar')
        version_node = SubElement(v_calendar_node, 'version')
        version_node.text = '2.0'
        prod_id_node = SubElement(v_calendar_node, 'prodid')
        prod_id_node.text = '-//fossasia//open-event//EN'
        cal_desc_node = SubElement(v_calendar_node, 'x-wr-caldesc')
        cal_desc_node.text = "Schedule for sessions at " + event.name
        cal_name_node = SubElement(v_calendar_node, 'x-wr-calname')
        cal_name_node.text = event.name

        sessions = Session.query \
            .filter_by(event_id=event_id) \
            .filter_by(state='accepted') \
            .filter(Session.deleted_at.is_(None)) \
            .order_by(asc(Session.starts_at)).all()

        for session in sessions:

            if session and session.starts_at and session.ends_at:

                v_event_node = SubElement(v_calendar_node, 'vevent')

                method_node = SubElement(v_event_node, 'method')
                method_node.text = 'PUBLISH'

                uid_node = SubElement(v_event_node, 'uid')
                uid_node.text = str(session.id) + "-" + event.identifier

                dtstart_node = SubElement(v_event_node, 'dtstart')
                dtstart_node.text = session.starts_at.isoformat()

                dtend_node = SubElement(v_event_node, 'dtend')
                dtend_node.text = session.ends_at.isoformat()

                duration_node = SubElement(v_event_node, 'duration')
                duration_node.text = str(session.ends_at - session.starts_at) + "00:00"

                summary_node = SubElement(v_event_node, 'summary')
                summary_node.text = session.title

                description_node = SubElement(v_event_node, 'description')
                description_node.text = session.short_abstract or 'N/A'

                class_node = SubElement(v_event_node, 'class')
                class_node.text = 'PUBLIC'

                status_node = SubElement(v_event_node, 'status')
                status_node.text = 'CONFIRMED'

                categories_node = SubElement(v_event_node, 'categories')
                categories_node.text = session.session_type.name if session.session_type else ''

                url_node = SubElement(v_event_node, 'url')
                url_node.text = url_for('v1.event_list',
                                        identifier=event.identifier, _external=True)

                location_node = SubElement(v_event_node, 'location')
                location_node.text = session.microlocation.name if session.microlocation else 'Not decided yet'

                for speaker in session.speakers:
                    attendee_node = SubElement(v_event_node, 'attendee')
                    attendee_node.text = speaker.name

        return tostring(i_calendar_node)
