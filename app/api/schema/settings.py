from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Schema

from app.api.helpers.utilities import dasherize
from app.settings import Environment
from utils.common import use_defaults


class SettingSchemaPublic(Schema):
    """
    Public Api schema for settings Model
    """
    class Meta:
        """
        Meta class for setting Api Schema
        """
        type_ = 'setting'
        self_view = 'v1.setting_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    id = fields.Str(dump_only=True)

    # Name of the application. (Eg. Event Yay!, Open Event)
    app_name = fields.Str(allow_none=True)

    # Tagline for the application. (Eg. Event Management and Ticketing, Home)
    tagline = fields.Str(allow_none=True)

    # Google Analytics
    analytics_key = fields.Str(allow_none=True)

    # FB
    fb_client_id = fields.Str(allow_none=True)

    #
    # Social links
    #
    google_url = fields.Str(allow_none=True)
    github_url = fields.Str(allow_none=True)
    twitter_url = fields.Str(allow_none=True)
    support_url = fields.Str(allow_none=True)
    facebook_url = fields.Str(allow_none=True)
    youtube_url = fields.Str(allow_none=True)

    # Url of Frontend
    frontend_url = fields.Url(allow_none=True)

    #
    # Cookie Policy
    #
    cookie_policy = fields.Str(allow_none=True)
    cookie_policy_link = fields.Str(allow_none=True)

    #
    # Online Payment Flags
    #
    is_paypal_activated = fields.Bool(dump_only=True)
    is_stripe_activated = fields.Bool(dump_only=True)


class SettingSchemaNonAdmin(SettingSchemaPublic):
    """
    Non Admin Api schema for settings Model
    """
    class Meta:
        """
        Meta class for setting Api Schema
        """
        type_ = 'setting'
        self_view = 'v1.setting_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    id = fields.Str(dump_only=True)

    # Stripe Keys
    stripe_client_id = fields.Str(allow_none=True)
    stripe_publishable_key = fields.Str(allow_none=True)

    #
    # Generators
    #
    android_app_url = fields.Str(allow_none=True)
    web_app_url = fields.Str(allow_none=True)


@use_defaults()
class SettingSchemaAdmin(SettingSchemaNonAdmin):
    """
    Admin Api schema for settings Model
    """
    class Meta:
        """
        Meta class for setting Api Schema
        """
        type_ = 'setting'
        self_view = 'v1.setting_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    id = fields.Str(dump_only=True)
    #
    # General
    #

    app_environment = fields.Str(default=Environment.PRODUCTION)

    # App secret
    secret = fields.Str(allow_none=True)
    # Static domain
    static_domain = fields.Str(allow_none=True)

    #
    #  STORAGE
    #

    # storage place, local, s3, .. can be more in future
    storage_place = fields.Str(allow_none=True)
    # S3
    aws_key = fields.Str(allow_none=True)
    aws_secret = fields.Str(allow_none=True)
    aws_bucket_name = fields.Str(allow_none=True)
    aws_region = fields.Str(allow_none=True)
    # Google Storage
    gs_key = fields.Str(allow_none=True)
    gs_secret = fields.Str(allow_none=True)
    gs_bucket_name = fields.Str(allow_none=True)

    #
    # Social Login
    #

    # Google Auth
    google_client_id = fields.Str(allow_none=True)
    google_client_secret = fields.Str(allow_none=True)
    # FB
    fb_client_id = fields.Str(allow_none=True)
    fb_client_secret = fields.Str(allow_none=True)
    # Twitter
    tw_consumer_key = fields.Str(allow_none=True)
    tw_consumer_secret = fields.Str(allow_none=True)
    # Instagram
    in_client_id = fields.Str(allow_none=True)
    in_client_secret = fields.Str(allow_none=True)

    #
    # Payment Gateway
    #

    # Stripe secret key
    stripe_secret_key = fields.Str(allow_none=True)

    # PayPal Credentials
    paypal_mode = fields.Str(allow_none=True)
    paypal_client = fields.Str(allow_none=True)
    paypal_secret = fields.Str(allow_none=True)
    paypal_sandbox_client = fields.Str(allow_none=True)
    paypal_sandbox_secret = fields.Str(allow_none=True)

    #
    # EMAIL
    #

    # Email service. (sendgrid,smtp)
    email_service = fields.Str(allow_none=True)
    email_from = fields.Str(allow_none=True)
    email_from_name = fields.Str(allow_none=True)
    # Sendgrid
    sendgrid_key = fields.Str(allow_none=True)
    # SMTP
    smtp_host = fields.Str(allow_none=True)
    smtp_username = fields.Str(allow_none=True)
    smtp_password = fields.Str(allow_none=True)
    smtp_port = fields.Integer(allow_none=True)
    smtp_encryption = fields.Str(allow_none=True)  # Can be tls, ssl, none
