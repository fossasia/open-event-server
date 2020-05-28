from sqlalchemy.ext.hybrid import hybrid_property

from app.models import db


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
    # Static domain
    static_domain = db.Column(db.String)
    # Order Expiry Time in Minutes
    order_expiry_time = db.Column(db.Integer, default=15, nullable=False)

    # Maximum number of complex custom fields allowed for a given form
    max_complex_custom_fields = db.Column(db.Integer, default=30, nullable=False)

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
    # CAPTCHA
    #

    # Google reCAPTCHA
    is_google_recaptcha_enabled = db.Column(db.Boolean, default=False, nullable=False)
    google_recaptcha_site = db.Column(db.String)
    google_recaptcha_secret = db.Column(db.String)

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
    stripe_test_client_id = db.Column(db.String)
    stripe_test_secret_key = db.Column(db.String)
    stripe_test_publishable_key = db.Column(db.String)

    # AliPay Keys - Stripe Sources
    alipay_secret_key = db.Column(db.String)
    alipay_publishable_key = db.Column(db.String)

    # Paypal credentials
    paypal_mode = db.Column(db.String)
    paypal_client = db.Column(db.String)
    paypal_secret = db.Column(db.String)
    paypal_sandbox_client = db.Column(db.String)
    paypal_sandbox_secret = db.Column(db.String)

    # Omise credentials
    omise_mode = db.Column(db.String)
    omise_live_public = db.Column(db.String)
    omise_live_secret = db.Column(db.String)
    omise_test_public = db.Column(db.String)
    omise_test_secret = db.Column(db.String)

    # payTM credentials
    is_paytm_activated = db.Column(db.Boolean, default=False, nullable=False)
    paytm_mode = db.Column(db.String)
    paytm_live_merchant = db.Column(db.String)
    paytm_live_secret = db.Column(db.String)
    paytm_sandbox_merchant = db.Column(db.String)
    paytm_sandbox_secret = db.Column(db.String)

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
    # Event Invoices settings
    #
    invoice_sending_day = db.Column(db.Integer, nullable=False, default=1)
    invoice_sending_timezone = db.Column(db.String, nullable=False, default="UTC")
    #
    # Admin Invoice Details
    #
    admin_billing_contact_name = db.Column(db.String)
    admin_billing_phone = db.Column(db.String)
    admin_billing_email = db.Column(db.String)
    admin_billing_country = db.Column(db.String)
    admin_billing_state = db.Column(db.String)
    admin_billing_tax_info = db.Column(db.String)
    admin_company = db.Column(db.String)
    admin_billing_address = db.Column(db.String)
    admin_billing_city = db.Column(db.String)
    admin_billing_zip = db.Column(db.String)
    admin_billing_additional_info = db.Column(db.String)
    #
    # Generators
    #
    android_app_url = db.Column(db.String)
    web_app_url = db.Column(db.String)

    frontend_url = db.Column(db.String, default="http://eventyay.com")

    #
    # Cookie Policy
    #
    cookie_policy = db.Column(
        db.String,
        default="This website, and certain approved third parties, use functional, "
        "analytical and tracking cookies (or similar technologies) to understand your "
        "event preferences and provide you with a customized experience. "
        "By closing this banner or by continuing to use the site, you agree. "
        "For more information please review our cookie policy.",
    )
    cookie_policy_link = db.Column(
        db.String, default="https://next.eventyay.com/cookie-policy"
    )

    @hybrid_property
    def is_paypal_activated(self):
        if (
            self.paypal_mode == 'sandbox'
            and self.paypal_sandbox_client
            and self.paypal_sandbox_secret
        ):
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

    @hybrid_property
    def is_alipay_activated(self):
        if self.alipay_publishable_key and self.alipay_secret_key:
            return True
        else:
            return False

    @hybrid_property
    def is_omise_activated(self):
        if (
            self.omise_mode == 'test'
            and self.omise_test_public
            and self.omise_test_secret
        ):
            return True
        elif self.omise_live_public and self.omise_live_secret:
            return True
        else:
            return False
