from app.helpers.versioning import clean_up_string, clean_html
from . import db


class UserDetail(db.Model):
    __tablename__ = "user_detail"
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String)
    lastname = db.Column(db.String)
    details = db.Column(db.String)
    avatar = db.Column(db.String)
    contact = db.Column(db.String)
    facebook = db.Column(db.String)
    twitter = db.Column(db.String)
    avatar_uploaded = db.Column(db.String)
    thumbnail = db.Column(db.String)
    small = db.Column(db.String)
    icon = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self,
                 firstname=None,
                 lastname=None,
                 avatar=None,
                 contact=None,
                 user_id=None,
                 facebook=None,
                 twitter=None,
                 thumbnail=None,
                 small=None,
                 icon=None,
                 avatar_uploaded=None):
        self.avatar = avatar
        self.contact = contact
        self.user_id = user_id
        self.facebook = facebook
        self.twitter = twitter
        self.thumbnail = thumbnail
        self.small = small
        self.icon = icon
        self.avatar_uploaded = avatar_uploaded

    def __repr__(self):
        return '<UserDetail %r>' % self.id

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return self.fullname

    def __setattr__(self, name, value):
        if name == 'details':
            super(UserDetail, self).__setattr__(name, clean_html(clean_up_string(value)))
        else:
            super(UserDetail, self).__setattr__(name, value)

    @property
    def fullname(self):
        firstname = self.firstname if self.firstname else ''
        lastname = self.lastname if self.lastname else ''
        if firstname and lastname:
            return u'{} {}'.format(firstname, lastname)
        else:
            return ''

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'id': self.id,
                'fullname': self.fullname,
                'avatar': self.avatar,
                'contact': self.contact,
                'facebook': self.facebook,
                'twitter': self.twitter,
                'thumbnail': self.thumbnail,
                'small': self.small,
                'icon': self.icon,
                'avatar_uploaded': self.avatar_uploaded}
