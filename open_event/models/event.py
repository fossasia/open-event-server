"""Copyright 2015 Rafal Kowalski"""
from sqlalchemy import event

from flask.ext import login
from open_event.helpers.date_formatter import DateFormatter
from open_event.helpers.versioning import clean_up_string, clean_html
from custom_forms import CustomForms, session_form_str, speaker_form_str
from open_event.models.email_notifications import EmailNotification
from . import db

class EventsUsers(db.Model):
    """Many to Many table Event Users"""
    __tablename__ = 'eventsusers'
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(
        db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    editor = db.Column(db.Boolean)
    admin = db.Column(db.Boolean)
    user = db.relationship("User", backref="events_assocs")


class Event(db.Model):
    """Event object table"""
    __tablename__ = 'events'
    __versioned__ = {
        'exclude': ['creator_id', 'schedule_published_on']
    }
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String)
    logo = db.Column(db.String)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    timezone = db.Column(db.String, nullable=False, default="UTC")
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    location_name = db.Column(db.String)
    searchable_location_name = db.Column(db.String)
    description = db.Column(db.Text)
    event_url = db.Column(db.String)
    background_url = db.Column(db.String)
    organizer_name = db.Column(db.String)
    organizer_url = db.Column(db.String)
    organizer_description = db.Column(db.String)
    in_trash = db.Column(db.Boolean, default=False)
    track = db.relationship('Track', backref="event")
    microlocation = db.relationship('Microlocation', backref="event")
    session = db.relationship('Session', backref="event")
    speaker = db.relationship('Speaker', backref="event")
    sponsor = db.relationship('Sponsor', backref="event")
    users = db.relationship("EventsUsers", backref="event")
    roles = db.relationship("UsersEventsRoles", backref="event")
    role_invites = db.relationship('RoleInvite', back_populates='event')
    privacy = db.Column(db.String, default="public")
    state = db.Column(db.String, default="Draft")
    closing_datetime = db.Column(db.DateTime)
    type = db.Column(db.String)
    topic = db.Column(db.String)
    sub_topic = db.Column(db.String)
    ticket_url = db.Column(db.String)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    creator = db.relationship('User')
    db.UniqueConstraint('track.name')
    code_of_conduct = db.Column(db.String)
    schedule_published_on = db.Column(db.DateTime)

    def __init__(self,
                 name=None,
                 logo=None,
                 start_time=None,
                 end_time=None,
                 timezone='UTC',
                 latitude=None,
                 longitude=None,
                 location_name=None,
                 email=None,
                 description=None,
                 event_url=None,
                 background_url=None,
                 organizer_name=None,
                 organizer_description=None,
                 state=None,
                 closing_datetime=None,
                 type=None,
                 privacy=None,
                 topic=None,
                 sub_topic=None,
                 ticket_url=None,
                 creator=None,
                 copyright=None,
                 code_of_conduct=None,
                 schedule_published_on=None,
                 in_trash=None,
                 searchable_location_name=None):
        self.name = name
        self.logo = logo
        self.email = email
        self.start_time = start_time
        self.end_time = end_time
        self.timezone = timezone
        self.latitude = latitude
        self.longitude = longitude
        self.location_name = location_name
        self.description = clean_up_string(description)
        self.event_url = event_url
        self.background_url = background_url
        self.organizer_name = organizer_name
        self.organizer_description = clean_up_string(organizer_description)
        self.state = state
        self.privacy = privacy
        self.closing_datetime = closing_datetime
        self.type = type
        self.topic = topic
        self.sub_topic = sub_topic
        self.ticket_url = ticket_url
        self.creator = creator
        self.copyright = copyright
        self.code_of_conduct = code_of_conduct
        self.schedule_published_on = schedule_published_on
        self.in_trash = in_trash
        self.searchable_location_name = searchable_location_name

    def __repr__(self):
        return '<Event %r>' % self.name

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return self.name

    def __setattr__(self, name, value):
        if name == 'organizer_description' or name == 'description' or name == 'code_of_conduct':
            super(Event, self).__setattr__(name, clean_html(clean_up_string(value)))
        else:
            super(Event, self).__setattr__(name, value)

    def notification_settings(self):
        try:
            return EmailNotification.query.filter_by(user_id=login.current_user.id).filter_by(event_id=self.id).first()
        except:
            return None

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'id': self.id,
            'name': self.name,
            'logo': self.logo,
            'begin': DateFormatter().format_date(self.start_time),
            'end': DateFormatter().format_date(self.end_time),
            'timezone': self.timezone,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'location_name': self.location_name,
            'email': self.email,
            'description': self.description,
            'event_url': self.event_url,
            'background_url': self.background_url,
            'organizer_name': self.organizer_name,
            'organizer_description': self.organizer_description,
            'privacy': self.privacy,
            'ticket_url': self.ticket_url,
            'code_of_conduct': self.code_of_conduct,
            'schedule_published_on': self.schedule_published_on
        }


# LISTENERS

@event.listens_for(Event, 'after_insert')
def receive_init(mapper, conn, target):
    custom_form = CustomForms(
        event_id=target.id,
        session_form=session_form_str,
        speaker_form=speaker_form_str
    )
    target.custom_forms.append(custom_form)
