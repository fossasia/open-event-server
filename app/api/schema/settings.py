from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Schema

from app.api.helpers.utilities import dasherize
from app.api.schema.base import TrimmedEmail
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

    # Order Expiry Time
    order_expiry_time = fields.Integer(
        allow_none=False, default=15, validate=lambda n: 1 <= n <= 60
    )

    # Start Page Event ID
    start_pg_event_id = fields.Str(allow_none=True, default=None)
    start_pg_enabled = fields.Str(allow_none=True, default='default')

    # Maximum number of complex custom fields allowed for a given form
    max_complex_custom_fields = fields.Integer(
        allow_none=False, default=30, validate=lambda n: 1 <= n <= 30
    )

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
    instagram_url = fields.Str(allow_none=True)
    patreon_url = fields.Str(allow_none=True)
    gitter_url = fields.Str(allow_none=True)
    telegram_url = fields.Str(allow_none=True)
    youtube_url = fields.Str(allow_none=True)
    weblate_url = fields.Str(allow_none=True)

    # Url of Frontend
    frontend_url = fields.Url(allow_none=True)

    rocket_chat_url = fields.Url(allow_none=True)

    #
    # Cookie Policy
    #
    cookie_policy = fields.Str(allow_none=True)
    cookie_policy_link = fields.Str(allow_none=True)

    #
    # Online Payment Flags
    #
    is_paytm_activated = fields.Bool(default=False)
    is_paypal_activated = fields.Bool(dump_only=True)
    is_stripe_activated = fields.Bool(dump_only=True)
    is_omise_activated = fields.Bool(dump_only=True)
    is_alipay_activated = fields.Bool(dump_only=True)
    is_billing_paypal_activated = fields.Bool(dump_only=True)

    #
    # Payment Gateways
    #

    # Stripe Credantials
    stripe_client_id = fields.Str(dump_only=True)
    stripe_publishable_key = fields.Str(dump_only=True)
    stripe_test_client_id = fields.Str(dump_only=True)
    stripe_test_publishable_key = fields.Str(dump_only=True)

    # PayPal Credentials
    paypal_mode = fields.Str(dump_only=True)
    paypal_client = fields.Str(dump_only=True)
    paypal_sandbox_client = fields.Str(dump_only=True)

    # Omise Credentials
    omise_mode = fields.Str(dump_only=True)
    omise_test_public = fields.Str(dump_only=True)
    omise_live_public = fields.Str(dump_only=True)

    # Alipay Credentials
    alipay_publishable_key = fields.Str(dump_only=True)

    # payTM credentials
    paytm_mode = fields.Str(dump_only=True)
    paytm_live_merchant = fields.Str(dump_only=True)
    paytm_sandbox_merchant = fields.Str(dump_only=True)

    # Admin Invoice Details
    admin_billing_contact_name = fields.Str(allow_none=True)
    admin_billing_phone = fields.Str(allow_none=True)
    admin_billing_email = TrimmedEmail(allow_none=True)
    admin_billing_state = fields.Str(allow_none=True)
    admin_billing_country = fields.Str(allow_none=True)
    admin_billing_tax_info = fields.Str(allow_none=True)
    admin_company = fields.Str(allow_none=True)
    admin_billing_address = fields.Str(allow_none=True)
    admin_billing_city = fields.Str(allow_none=True)
    admin_billing_zip = fields.Str(allow_none=True)
    admin_billing_additional_info = fields.Str(allow_none=True)
    admin_billing_logo = fields.Url(allow_none=True)

    #
    # image and slide size
    #
    logo_size = fields.Integer(allow_none=False, default=1000)
    image_size = fields.Integer(allow_none=False, default=10000)
    slide_size = fields.Integer(allow_none=False, default=20000)


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
    # CAPTCHA
    #

    # Google reCAPTCHA
    is_google_recaptcha_enabled = fields.Bool(allow_none=False, default=False)
    google_recaptcha_site = fields.Str(allow_none=True)
    google_recaptcha_secret = fields.Str(allow_none=True)

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
    # Payment Gateways
    #

    # Stripe Credantials
    stripe_client_id = fields.Str(allow_none=True)
    stripe_publishable_key = fields.Str(allow_none=True)
    stripe_secret_key = fields.Str(allow_none=True)
    stripe_test_client_id = fields.Str(allow_none=True)
    stripe_test_secret_key = fields.Str(allow_none=True)
    stripe_test_publishable_key = fields.Str(allow_none=True)

    # PayPal Credentials
    paypal_mode = fields.Str(allow_none=True)
    paypal_client = fields.Str(allow_none=True)
    paypal_secret = fields.Str(allow_none=True)
    paypal_sandbox_client = fields.Str(allow_none=True)
    paypal_sandbox_secret = fields.Str(allow_none=True)

    # Omise Credentials
    omise_mode = fields.Str(allow_none=True)
    omise_test_public = fields.Str(allow_none=True)
    omise_test_secret = fields.Str(allow_none=True)
    omise_live_public = fields.Str(allow_none=True)
    omise_live_secret = fields.Str(allow_none=True)

    # Alipay Credentials
    alipay_publishable_key = fields.Str(allow_none=True)
    alipay_secret_key = fields.Str(allow_none=True)

    # payTM credentials
    paytm_mode = fields.Str(allow_none=True)
    paytm_live_merchant = fields.Str(allow_none=True)
    paytm_live_secret = fields.Str(allow_none=True)
    paytm_sandbox_merchant = fields.Str(allow_none=True)
    paytm_sandbox_secret = fields.Str(allow_none=True)
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

    rocket_chat_registration_secret = fields.Str(allow_none=True)

    # Event Invoices settings
    invoice_sending_day = fields.Integer(allow_none=False, default=1)
    invoice_sending_timezone = fields.Str(allow_none=False, default="UTC")

    # Admin Invoice Details
    admin_billing_paypal_email = TrimmedEmail(allow_none=True)
