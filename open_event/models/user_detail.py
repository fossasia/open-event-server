from . import db


class UserDetail(db.Model):
    __tablename__ = "user_detail"
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String)
    details = db.Column(db.String)
    avatar = db.Column(db.String)
    contact = db.Column(db.String)
    facebook = db.Column(db.String)
    twitter = db.Column(db.String)
    avatar_uploaded = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self,
                 fullname=None,
                 avatar=None,
                 contact=None,
                 user_id=None,
                 facebook=None,
                 twitter=None,
                 avatar_uploaded=None):
        self.fullname = fullname
        self.avatar = avatar
        self.contact = contact
        self.user_id = user_id
        self.facebook = facebook
        self.twitter = twitter
        self.avatar_uploaded = avatar_uploaded

    def __repr__(self):
        return '<UserDetail %r>' % self.id

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return self.fullname

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {'id': self.id,
                'fullname': self.fullname,
                'avatar': self.avatar,
                'contact': self.contact,
                'facebook': self.facebook,
                'twitter': self.twitter,
                'avatar_uploaded':self.avatar_uploaded}
