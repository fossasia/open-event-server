from . import db


class Setting(db.Model):
    __tablename__ = 'settings'
    id = db.Column(db.Integer, primary_key=True)
    # S3
    aws_key = db.Column(db.String)
    aws_secret = db.Column(db.String)
    aws_bucket_name = db.Column(db.String)
    # Google Auth
    google_client_id = db.Column(db.String)
    google_client_secret = db.Column(db.String)
    # FB
    fb_client_id = db.Column(db.String)
    fb_client_secret = db.Column(db.String)
    # Sendgrid
    sendgrid_key = db.Column(db.String)
    # App secret
    secret = db.Column(db.String)
    # storage place, local, aws, .. can be more in future
    storage_place = db.Column(db.String)

    def __init__(self, aws_key=None, aws_secret=None, aws_bucket_name=None,
                 google_client_id=None, google_client_secret=None,
                 fb_client_id=None, fb_client_secret=None, sendgrid_key=None,
                 secret=None, storage_place=None):
        self.aws_key = aws_key
        self.aws_secret = aws_secret
        self.aws_bucket_name = aws_bucket_name
        self.google_client_id = google_client_id
        self.google_client_secret = google_client_secret
        self.fb_client_id = fb_client_id
        self.fb_client_secret = fb_client_secret
        self.sendgrid_key = sendgrid_key
        self.secret = secret
        self.storage_place = storage_place

    def __repr__(self):
        return 'Settings'

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return 'Settings'
