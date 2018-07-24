import factory

import app.factories.common as common
from app.models.setting import db, Setting


class SettingFactory(factory.alchemy.SQLAlchemyModelFactory):

    class Meta:
        model = Setting
        sqlalchemy_session = db.session

    app_environment = common.environment_
    # Name of the application. (Eg. Event Yay!, Open Event)
    app_name = common.string_
    # Tagline for the application. (Eg. Event Management and Ticketing, Home)
    tagline = common.string_
    # App secret
    secret = common.secret_
    # Static domain
    static_domain = common.url_

    #
    #  STORAGE
    #

    # storage place, local, s3, .. can be more in future
    storage_place = common.string_
    # S3
    aws_key = common.string_
    aws_secret = common.string_
    aws_bucket_name = common.string_
    aws_region = common.string_
    # Google Storage
    gs_key = common.string_
    gs_secret = common.string_
    gs_bucket_name = common.string_

    #
    # Social Login
    #

    # Google Auth
    google_client_id = common.string_
    google_client_secret = common.string_
    # FB
    fb_client_id = common.string_
    fb_client_secret = common.string_
    # Twitter
    tw_consumer_key = common.string_
    tw_consumer_secret = common.string_
    # Instagram
    in_client_id = common.string_
    in_client_secret = common.string_

    #
    # Payment Gateway
    #

    # Stripe Keys
    stripe_client_id = common.string_
    stripe_secret_key = common.string_
    stripe_publishable_key = common.string_
    # PayPal Credentials
    paypal_mode = 'development'
    paypal_client = common.string_
    paypal_secret = common.string_
    paypal_sandbox_client = common.string_
    paypal_sandbox_secret = common.string_
    #
    # EMAIL
    #

    # Email service. (sendgrid,smtp)
    email_service = common.string_
    email_from = common.string_
    email_from_name = common.string_
    # Sendgrid
    sendgrid_key = common.string_
    # SMTP
    smtp_host = common.string_
    smtp_username = common.string_
    smtp_password = common.string_
    smtp_port = common.integer_
    smtp_encryption = common.string_  # Can be tls, ssl, none
    # Google Analytics
    analytics_key = common.string_

    #
    # Social links
    #
    google_url = common.url_
    github_url = common.url_
    twitter_url = common.url_
    support_url = common.url_
    facebook_url = common.url_
    youtube_url = common.url_

    #
    # Generators
    #
    android_app_url = common.url_
    web_app_url = common.url_

    frontend_url = common.url_

    #
    # Cookie Policy
    #
    cookie_policy = common.string_
    cookie_policy_link = common.url_
