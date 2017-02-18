import re
from datetime import datetime

import arrow
import humanize
from flask import request
from forex_python.converter import CurrencyCodes
from nameparser import HumanName
from pytz import timezone

from app.helpers.data_getter import DataGetter
from app.helpers.flask_ext.helpers import camel_case, slugify


def init_filters(app):
    @app.template_filter('pretty_name')
    def pretty_name_filter(string):
        string = str(string)
        string = string.replace('_', ' ')
        string = string.title()
        return string

    @app.template_filter('currency_symbol')
    def currency_symbol_filter(currency_code):
        symbol = CurrencyCodes().get_symbol(currency_code)
        return symbol if symbol else '$'

    @app.template_filter('currency_name')
    def currency_name_filter(currency_code):
        name = CurrencyCodes().get_currency_name(currency_code)
        return name if name else ''

    @app.template_filter('camel_case')
    def camel_case_filter(string):
        return camel_case(string)

    @app.template_filter('slugify')
    def slugify_filter(string):
        return slugify(string)

    @app.template_filter('humanize')
    def humanize_filter(time):
        if not time:
            return "N/A"
        return arrow.get(time).humanize()

    @app.template_filter('humanize_alt')
    def humanize_alt_filter(time):
        if not time:
            return "N/A"
        return humanize.naturaltime(datetime.now() - time)

    @app.template_filter('time_format')
    def time_filter(time):
        if not time:
            return "N/A"
        return time

    @app.template_filter('firstname')
    def firstname_filter(string):
        if string:
            return HumanName(string).first
        else:
            return 'N/A'

    @app.template_filter('middlename')
    def middlename_filter(string):
        if string:
            return HumanName(string).middle
        else:
            return 'N/A'

    @app.template_filter('lastname')
    def lastname_filter(string):
        if string:
            return HumanName(string).last
        else:
            return 'N/A'

    @app.template_filter('money')
    def money_filter(string):
        return '{:20,.2f}'.format(float(string))

    @app.template_filter('datetime')
    def simple_datetime_display(date):
        return date.strftime('%B %d, %Y %I:%M %p')

    @app.template_filter('external_url')
    def external_url(url):
        """Returns an external URL for the given `url`.
        If URL is already external, it remains unchanged.
        """
        url_pattern = r'^(https?)://.*$'
        scheme = re.match(url_pattern, url)
        if not scheme:
            url_root = request.url_root.rstrip('/')
            return '{}{}'.format(url_root, url)
        else:
            return url

    @app.template_filter('localize_dt')
    def localize_dt(dt, tzname):
        """Accepts a Datetime object and a Timezone name.
        Returns Timezone aware Datetime.
        """
        localized_dt = timezone(tzname).localize(dt)
        return localized_dt.isoformat()

    @app.template_filter('localize_dt_obj')
    def localize_dt_obj(dt, tzname):
        """Accepts a Datetime object and a Timezone name.
        Returns Timezone aware Datetime Object.
        """
        localized_dt = timezone(tzname).localize(dt)
        return localized_dt

    @app.template_filter('as_timezone')
    def as_timezone(dt, tzname):
        """Accepts a Time aware Datetime object and a Timezone name.
            Returns Converted Timezone aware Datetime Object.
            """
        if tzname:
            if timezone(tzname):
                return dt.astimezone(timezone(tzname))
        return dt

    @app.template_filter('fees_by_currency')
    def fees_by_currency(currency):
        """Returns a fees object according to the currency input"""
        fees = DataGetter.get_fee_settings_by_currency(currency)
        return fees

    @app.template_filter('filename_from_url')
    def filename_from_url(url):
        if url:
            return url.rsplit('/', 1)[1]
        return ""
