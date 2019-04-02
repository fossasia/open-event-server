from app.models import db
from sqlalchemy.ext.hybrid import hybrid_property


class Environment:

    def __init__(self):
        pass

    DEVELOPMENT = 'development'
    STAGING = 'staging'
    PRODUCTION = 'production'
    TESTING = 'testing'


class Setting(db.Model):
    __tablename__ = 'settings'
    id = db.Column(db.Integer, primary_key=True)

    #
    # General
    #

    app_environment = db.Column(db.String, default=Environment.PRODUCTION)
    # Name of the application. (Eg. Event Yay!, Open Event)
    app_name = db.Column(db.String)
    # Tagline for the application. (Eg. Event Management and Ticketing, Home)
    tagline = db.Column(db.String)
    # App secret
    secret = db.Column(db.String)
    # Static domain
    static_domain = db.Column(db.String)

    #
    #  STORAGE
    #

    # storage place, local, s3, .. can be more in future
    storage_place = db.Column(db.String)
    # S3
    aws_key = db.Column(db.String)
    aws_secret = db.Column(db.String)
    aws_bucket_name = db.Column(db.String)
    aws_region = db.Column(db.String)
    # Google Storage
    gs_key = db.Column(db.String)
    gs_secret = db.Column(db.String)
    gs_bucket_name = db.Column(db.String)

    #
    # Social Login
    #

    # Google Auth
    google_client_id = db.Column(db.String)
    google_client_secret = db.Column(db.String)
    # FB
    fb_client_id = db.Column(db.String)
    fb_client_secret = db.Column(db.String)
    # Twitter
    tw_consumer_key = db.Column(db.String)
    tw_consumer_secret = db.Column(db.String)
    # Instagram
    in_client_id = db.Column(db.String)
    in_client_secret = db.Column(db.String)

    #
    # Payment Gateway
    #

    # Stripe Keys
    stripe_client_id = db.Column(db.String)
    stripe_secret_key = db.Column(db.String)
    stripe_publishable_key = db.Column(db.String)

    # Paypal credentials
    paypal_mode = db.Column(db.String)
    paypal_client = db.Column(db.String)
    paypal_secret = db.Column(db.String)
    paypal_sandbox_client = db.Column(db.String)
    paypal_sandbox_secret = db.Column(db.String)

    #
    # EMAIL
    #

    # Email service. (sendgrid,smtp)
    email_service = db.Column(db.String)
    email_from = db.Column(db.String)
    email_from_name = db.Column(db.String)
    # Sendgrid
    sendgrid_key = db.Column(db.String)
    # SMTP
    smtp_host = db.Column(db.String)
    smtp_username = db.Column(db.String)
    smtp_password = db.Column(db.String)
    smtp_port = db.Column(db.Integer)
    smtp_encryption = db.Column(db.String)  # Can be tls, ssl, none
    # Google Analytics
    analytics_key = db.Column(db.String)

    #
    # Social links
    #
    google_url = db.Column(db.String)
    github_url = db.Column(db.String)
    twitter_url = db.Column(db.String)
    support_url = db.Column(db.String)
    facebook_url = db.Column(db.String)
    youtube_url = db.Column(db.String)

    #
    # Generators
    #
    android_app_url = db.Column(db.String)
    web_app_url = db.Column(db.String)

    frontend_url = db.Column(db.String, default="http://eventyay.com")

    #
    # Cookie Policy
    #
    cookie_policy = db.Column(db.String,
                              default="This website, and certain approved third parties, use functional, "
                                      "analytical and tracking cookies (or similar technologies) to understand your "
                                      "event preferences and provide you with a customized experience. "
                                      "By closing this banner or by continuing to use the site, you agree. "
                                      "For more information please review our cookie policy.")
    cookie_policy_link = db.Column(db.String, default="https://next.eventyay.com/cookie-policy")

    def __init__(self,
                 app_environment=Environment.PRODUCTION,
                 aws_key=None,
                 aws_secret=None,
                 aws_bucket_name=None,
                 aws_region=None,
                 gs_key=None,
                 gs_secret=None,
                 gs_bucket_name=None,
                 google_client_id=None, google_client_secret=None,
                 fb_client_id=None, fb_client_secret=None, tw_consumer_key=None,
                 stripe_client_id=None,
                 stripe_secret_key=None, stripe_publishable_key=None,
                 in_client_id=None, in_client_secret=None,
                 tw_consumer_secret=None, sendgrid_key=None,
                 secret=None, storage_place=None,
                 app_name=None,
                 static_domain=None,
                 tagline=None,
                 google_url=None, github_url=None,
                 twitter_url=None, support_url=None,
                 analytics_key=None,
                 paypal_mode=None,
                 paypal_client=None,
                 paypal_secret=None,
                 paypal_sandbox_client=None,
                 paypal_sandbox_secret=None,
                 email_service=None,
                 email_from=None,
                 email_from_name=None,
                 smtp_host=None,
                 smtp_username=None,
                 smtp_password=None,
                 smtp_port=None,
                 smtp_encryption=None,
                 frontend_url=None,
                 facebook_url=None,
                 youtube_url=None,
                 android_app_url=None,
                 web_app_url=None,
                 cookie_policy=None,
                 cookie_policy_link=None):
        self.app_environment = app_environment
        self.aws_key = aws_key
        self.aws_secret = aws_secret
        self.aws_bucket_name = aws_bucket_name
        self.aws_region = aws_region

        self.gs_key = gs_key
        self.gs_secret = gs_secret
        self.gs_bucket_name = gs_bucket_name

        self.google_client_id = google_client_id
        self.google_client_secret = google_client_secret
        self.fb_client_id = fb_client_id
        self.fb_client_secret = fb_client_secret
        self.tw_consumer_key = tw_consumer_key
        self.tw_consumer_secret = tw_consumer_secret
        self.in_client_id = in_client_id
        self.in_client_secret = in_client_secret
        self.sendgrid_key = sendgrid_key
        self.analytics_key = analytics_key
        self.app_name = app_name
        self.static_domain = static_domain
        self.tagline = tagline
        self.secret = secret
        self.storage_place = storage_place
        self.google_url = google_url
        self.github_url = github_url
        self.twitter_url = twitter_url
        self.support_url = support_url
        self.facebook_url = facebook_url
        self.youtube_url = youtube_url
        self.stripe_client_id = stripe_client_id
        self.stripe_publishable_key = stripe_publishable_key
        self.stripe_secret_key = stripe_secret_key
        self.web_app_url = web_app_url
        self.android_app_url = android_app_url
        self.email_service = email_service
        self.smtp_host = smtp_host
        self.smtp_username = smtp_username
        self.smtp_password = smtp_password
        self.smtp_port = smtp_port
        self.smtp_encryption = smtp_encryption
        self.email_from = email_from
        self.email_from_name = email_from_name
        self.frontend_url = frontend_url
        self.cookie_policy = cookie_policy
        self.cookie_policy_link = cookie_policy_link

        # Paypal credentials
        self.paypal_mode = paypal_mode
        self.paypal_client = paypal_client
        self.paypal_secret = paypal_secret
        self.paypal_sandbox_client = paypal_sandbox_client
        self.paypal_sandbox_secret = paypal_sandbox_secret

    @hybrid_property
    def is_paypal_activated(self):
        if self.paypal_mode == 'sandbox' and self.paypal_sandbox_client and self.paypal_sandbox_secret:
            return True
        elif self.paypal_client and self.paypal_secret:
            return True
        else:
            return False

    @hybrid_property
    def is_stripe_activated(self):
        return self.stripe_client_id is not None

    def __repr__(self):
        return 'Settings'

    def __str__(self):
        return self.__repr__()
