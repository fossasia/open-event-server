from . import db

SPEAKER = 'speaker'
ADMIN = 'admin'
ORGANIZER = 'organizer'
SUPERADMIN = 'super_admin'


class User(db.Model):
    """User model class"""
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(100))
    login = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(128))
    reset_password = db.Column(db.String(128))
    salt = db.Column(db.String(128))
    role = db.Column(db.String())
    avatar = db.Column(db.String(600))
    tokens = db.Column(db.Text)

    # Flask-Login integration
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    def is_super_admin(self):
        return self.role == SUPERADMIN

    def is_admin(self):
        return self.role == ORGANIZER

    def is_organizer(self):
        return self.role == ADMIN

    def is_speaker(self):
        return self.role == SPEAKER

    # Required for administrative interface
    def __unicode__(self):
        return self.username
