from app.models.setting import Setting
from tests.factories import common
from tests.factories.base import BaseFactory


class SettingFactory(BaseFactory):
    class Meta:
        model = Setting

    app_environment = common.environment_
    # Name of the application. (Eg. Event Yay!, Open Event)
    app_name = common.string_
    # Tagline for the application. (Eg. Event Management and Ticketing, Home)
    tagline = common.string_
    # Static domain
    static_domain = common.url_
    # Order Expiry Time
    order_expiry_time = 15  # min

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
    stripe_test_secret_key = common.string_
    stripe_test_publishable_key = common.string_
    stripe_mode = 'development'
    # PayPal Credentials
    paypal_mode = 'development'
    paypal_client = common.string_
    paypal_secret = common.string_
    paypal_sandbox_client = common.string_
    paypal_sandbox_secret = common.string_
    # Omise Credentials
    omise_mode = 'development'
    omise_test_public = common.string_
    omise_test_secret = common.string_
    omise_live_public = common.string_
    omise_live_secret = common.string_
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

    # Event Invoices settings
    invoice_sending_day = common.integer_
    invoice_sending_timezone = common.timezone_

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

    # Admin Invoice Details
    admin_billing_contact_name = common.string_
    admin_billing_phone = common.string_
    admin_billing_email = common.email_
    admin_billing_state = common.string_
    admin_billing_country = common.string_
    admin_billing_tax_info = common.string_
    admin_company = common.string_
    admin_billing_address = common.string_
    admin_billing_city = common.string_
    admin_billing_zip = common.string_
    admin_billing_additional_info = common.string_
