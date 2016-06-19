"""Copyright 2015 Rafal Kowalski"""
from . import db


class Speaker(db.Model):
    """Speaker model class"""
    __tablename__ = 'speaker'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    photo = db.Column(db.String)
    short_biography = db.Column(db.Text)
    long_biography = db.Column(db.Text)
    email = db.Column(db.String, nullable=False)
    mobile = db.Column(db.String)
    website = db.Column(db.String)
    twitter = db.Column(db.String)
    facebook = db.Column(db.String)
    github = db.Column(db.String)
    linkedin = db.Column(db.String)
    organisation = db.Column(db.String, nullable=False)
    position = db.Column(db.String)
    country = db.Column(db.String, nullable=False)
    event_id = db.Column(
        db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref='speakers')

    def __init__(self,
                 name=None,
                 photo=None,
                 short_biography=None,
                 long_biography=None,
                 email=None,
                 mobile=None,
                 website=None,
                 twitter=None,
                 facebook=None,
                 github=None,
                 linkedin=None,
                 organisation=None,
                 position=None,
                 country=None,
                 event_id=None,
                 user=None):
        self.name = name
        self.photo = photo
        self.short_biography = short_biography
        self.long_biography = long_biography
        self.email = email
        self.mobile = mobile
        self.website = website
        self.twitter = twitter
        self.facebook = facebook
        self.github = github
        self.linkedin = linkedin
        self.organisation = organisation
        self.position = position
        self.country = country
        self.event_id = event_id
        self.user = user

    @staticmethod
    def get_service_name():
        return 'speaker'

    def __repr__(self):
        return '<Speaker %r>' % self.name

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return self.name

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""

        session_data = [{'title': session.title, 'id': session.id}
                        for session in self.sessions]

        return {
            'id': self.id,
            'name': self.name,
            'photo': self.photo,
            'short_biography': self.short_biography,
            'long_biography': self.long_biography,
            'email': self.email,
            'mobile': self.mobile,
            'website': self.website,
            'twitter': self.twitter,
            'facebook': self.facebook,
            'github': self.github,
            'linkedin': self.linkedin,
            'organisation': self.organisation,
            'position': self.position,
            'country': self.country,
            'sessions': session_data
        }
