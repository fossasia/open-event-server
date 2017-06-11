from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from marshmallow_jsonapi.flask import Schema, Relationship
from marshmallow_jsonapi import fields
from app.models import db
from app.api.helpers.permissions import jwt_required, is_admin, is_user_itself
from flask_jwt import current_identity
from sqlalchemy.orm.exc import NoResultFound
from flask_rest_jsonapi.exceptions import ObjectNotFound
from app.models.event import Event
from app.models.setting import Setting


class Environment:

    def __init__(self):
        pass

    DEVELOPMENT = 'development'
    STAGING = 'staging'
    PRODUCTION = 'production'
    TESTING = 'testing'


class SettingSchemaAdmin(Schema):
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

    id = fields.Str(dump_only=True)
    #
    # General
    #

    app_environment = fields.Str(default=Environment.PRODUCTION)
    # Name of the application. (Eg. Event Yay!, Open Event)
    app_name = fields.Str()
    # Tagline for the application. (Eg. Event Management and Ticketing, Home)
    tagline = fields.Str()
    # App secret
    secret = fields.Str()

    #
    #  STORAGE
    #

    # storage place, local, s3, .. can be more in future
    storage_place = fields.Str()
    # S3
    aws_key = fields.Str()
    aws_secret = fields.Str()
    aws_bucket_name = fields.Str()
    aws_region = fields.Str()
    # Google Storage
    gs_key = fields.Str()
    gs_secret = fields.Str()
    gs_bucket_name = fields.Str()

    #
    # Social Login
    #

    # Google Auth
    google_client_id = fields.Str()
    google_client_secret = fields.Str()
    # FB
    fb_client_id = fields.Str()
    fb_client_secret = fields.Str()
    # Twitter
    tw_consumer_key = fields.Str()
    tw_consumer_secret = fields.Str()
    # Instagram
    in_client_id = fields.Str()
    in_client_secret = fields.Str()

    #
    # Payment Gateway
    #

    # Stripe Keys
    stripe_client_id = fields.Str()
    stripe_secret_key = fields.Str()
    stripe_publishable_key = fields.Str()
    # PayPal Credentials
    paypal_mode = fields.Str()
    paypal_sandbox_username = fields.Str()
    paypal_sandbox_password = fields.Str()
    paypal_sandbox_signature = fields.Str()
    paypal_live_username = fields.Str()
    paypal_live_password = fields.Str()
    paypal_live_signature = fields.Str()

    #
    # EMAIL
    #

    # Email service. (sendgrid,smtp)
    email_service = fields.Str()
    email_from = fields.Str()
    email_from_name = fields.Str()
    # Sendgrid
    sendgrid_key = fields.Str()
    # SMTP
    smtp_host = fields.Str()
    smtp_username = fields.Str()
    smtp_password = fields.Str()
    smtp_port = fields.Integer()
    smtp_encryption = fields.Str()  # Can be tls, ssl, none
    # Google Analytics
    analytics_key = fields.Str()

    #
    # Social links
    #
    google_url = fields.Str()
    github_url = fields.Str()
    twitter_url = fields.Str()
    support_url = fields.Str()
    facebook_url = fields.Str()
    youtube_url = fields.Str()

    #
    # Generators
    #
    android_app_url = fields.Str()
    web_app_url = fields.Str()


class SettingSchemaNonAdmin(Schema):
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

    id = fields.Str(dump_only=True)

    # Name of the application. (Eg. Event Yay!, Open Event)
    app_name = fields.Str()
    # Tagline for the application. (Eg. Event Management and Ticketing, Home)
    tagline = fields.Str()
    # Google Analytics
    analytics_key = fields.Str()


class SettingDetail(ResourceDetail):
    """
    setting detail by id
    """

    def before_get(self, args, kwargs):
        kwargs['id'] = 1
        if current_identity.is_admin or current_identity.is_super_admin:
            self.schema = SettingSchemaAdmin
        else:
            self.schema = SettingSchemaNonAdmin

    def before_patch(self, args, kwargs):
        kwargs['id'] = 1

    decorators = (jwt_required, )
    methods = ['GET', 'PATCH']
    patch = is_admin(ResourceDetail.patch.__func__)
    schema = SettingSchemaAdmin
    data_layer = {'session': db.session,
                  'model': Setting}
