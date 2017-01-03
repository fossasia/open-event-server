from app.helpers.versioning import clean_up_string, clean_html
from . import db
from ..helpers.helpers import ensure_social_link


class Speaker(db.Model):
    """Speaker model class"""
    __tablename__ = 'speaker'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    photo = db.Column(db.String)
    thumbnail = db.Column(db.String)
    small = db.Column(db.String)
    icon = db.Column(db.String)
    short_biography = db.Column(db.Text)
    long_biography = db.Column(db.Text)
    speaking_experience = db.Column(db.Text)
    email = db.Column(db.String, nullable=False)
    mobile = db.Column(db.String)
    website = db.Column(db.String)
    twitter = db.Column(db.String)
    facebook = db.Column(db.String)
    github = db.Column(db.String)
    linkedin = db.Column(db.String)
    organisation = db.Column(db.String, nullable=False)
    featured = db.Column(db.Boolean, default=False)
    position = db.Column(db.String)
    country = db.Column(db.String, nullable=False)
    city = db.Column(db.String)
    heard_from = db.Column(db.String)
    sponsorship_required = db.Column(db.Text)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='SET NULL'))
    user = db.relationship('User', backref='speakers')

    def __init__(self,
                 name=None,
                 photo=None,
                 thumbnail=None,
                 small=None,
                 icon=None,
                 short_biography=None,
                 long_biography=None,
                 speaking_experience=None,
                 email=None,
                 mobile=None,
                 website=None,
                 twitter=None,
                 facebook=None,
                 github=None,
                 linkedin=None,
                 organisation=None,
                 featured=False,
                 position=None,
                 country=None,
                 city=None,
                 heard_from=None,
                 sponsorship_required=None,
                 event_id=None,
                 user=None):
        self.name = name
        self.photo = photo
        self.thumbnail = thumbnail
        self.small = small
        self.icon = icon
        self.short_biography = short_biography
        self.long_biography = long_biography
        self.speaking_experience = speaking_experience
        self.email = email
        self.mobile = mobile
        self.website = website
        self.twitter = twitter
        self.facebook = facebook
        self.github = github
        self.linkedin = linkedin
        self.featured = featured
        self.organisation = organisation
        self.position = position
        self.country = country
        self.city = city
        self.heard_from = heard_from
        self.sponsorship_required = sponsorship_required
        self.event_id = event_id
        # ensure links are in social fields
        self.ensure_social_links()
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

    def __setattr__(self, name, value):
        if name == 'short_biography' or name == 'long_biography' or name == 'speaking_experience' or name == 'sponsorship_required':
            super(Speaker, self).__setattr__(name, clean_html(clean_up_string(value)))
        else:
            super(Speaker, self).__setattr__(name, value)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""

        session_data = [{'title': session.title, 'id': session.id}
                        for session in self.sessions]

        return {
            'id': self.id,
            'name': self.name,
            'photo': self.photo,
            'thumbnail': self.thumbnail,
            'small': self.small,
            'icon': self.icon,
            'short_biography': self.short_biography,
            'long_biography': self.long_biography,
            'speaking_experience': self.speaking_experience,
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
            'city': self.city,
            'heard_from': self.heard_from,
            'sponsorship_required': self.sponsorship_required,
            'sessions': session_data
        }

    def ensure_social_links(self):
        """convert usernames in social network fields to full links"""
        self.twitter = ensure_social_link('https://twitter.com', self.twitter)
        self.facebook = ensure_social_link('https://www.facebook.com', self.facebook)
        self.github = ensure_social_link('https://github.com', self.github)
        self.linkedin = ensure_social_link('https://www.linkedin.com/in', self.linkedin)
