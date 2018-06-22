from app.models.base import SoftDeletionModel
from app.models.helpers.versioning import clean_up_string, clean_html
from app.models import db


class Speaker(SoftDeletionModel):
    """Speaker model class"""
    __tablename__ = 'speaker'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    photo_url = db.Column(db.String)
    thumbnail_image_url = db.Column(db.String)
    small_image_url = db.Column(db.String)
    icon_image_url = db.Column(db.String)
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
    organisation = db.Column(db.String)
    is_featured = db.Column(db.Boolean, default=False)
    position = db.Column(db.String)
    country = db.Column(db.String)
    city = db.Column(db.String)
    gender = db.Column(db.String)
    heard_from = db.Column(db.String)
    sponsorship_required = db.Column(db.Text)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'))

    def __init__(self,
                 name=None,
                 photo_url=None,
                 thumbnail_image_url=None,
                 small_image_url=None,
                 icon_image_url=None,
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
                 is_featured=False,
                 position=None,
                 country=None,
                 city=None,
                 gender=None,
                 heard_from=None,
                 sponsorship_required=None,
                 event_id=None,
                 user_id=None,
                 deleted_at=None):
        self.name = name
        self.photo_url = photo_url
        self.thumbnail_image_url = thumbnail_image_url
        self.small_image_url = small_image_url
        self.icon_image_url = icon_image_url
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
        self.is_featured = is_featured
        self.organisation = organisation
        self.position = position
        self.country = country
        self.city = city
        self.gender = gender
        self.heard_from = heard_from
        self.sponsorship_required = sponsorship_required
        self.event_id = event_id
        self.user_id = user_id
        self.deleted_at = deleted_at

    @staticmethod
    def get_service_name():
        return 'speaker'

    def __repr__(self):
        return '<Speaker %r>' % self.name

    def __str__(self):
        return self.__repr__()

    def __setattr__(self, name, value):
        if name == 'short_biography' or name == 'long_biography' or name == 'speaking_experience' or name == 'sponsorship_required':
            super(Speaker, self).__setattr__(name, clean_html(clean_up_string(value)))
        else:
            super(Speaker, self).__setattr__(name, value)

    @property
    def serialize(self):
        """Return object data in easily serializable format"""

        session_data = [{'title': session.title, 'id': session.id}
                        for session in self.sessions]

        return {
            'id': self.id,
            'name': self.name,
            'photo_url': self.photo_url,
            'thumbnail_image_url': self.thumbnail_image_url,
            'small_image_url': self.small_image_url,
            'icon_image_url': self.icon_image_url,
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
            'gender': self.gender,
            'heard_from': self.heard_from,
            'sponsorship_required': self.sponsorship_required,
            'sessions': session_data
        }
