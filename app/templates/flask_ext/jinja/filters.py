from datetime import datetime

import humanize
import pytz
from forex_python.converter import CurrencyCodes

from app.api.helpers.mail import convert_to_user_locale
from app.api.helpers.utilities import strip_tags


def humanize_helper(time):
    """Returns time passed from now in a human readable duration"""

    if not time:
        return "N/A"
    return humanize.naturaltime(datetime.now(pytz.utc) - time.astimezone(pytz.utc))


def init_filters(app):
    @app.template_filter('currency_symbol')
    def currency_symbol_filter(currency_code):
        symbol = CurrencyCodes().get_symbol(currency_code)
        return symbol if symbol else currency_code

    @app.template_filter('money')
    def money_filter(amount, email, currency):
        return convert_to_user_locale(email, amount=amount, currency=currency)

    @app.template_filter('datetime')
    def simple_datetime_display(date, timezone=None, format='%B %d, %Y %H:%M (%Z%z)'):
        if not date:
            return ''
        if timezone:
            date = date.replace(tzinfo=pytz.timezone('UTC')).astimezone(
                pytz.timezone(timezone)
            )
        return date.strftime(format)

    @app.template_filter('date')
    def simple_date_display(date, timezone=None):
        return simple_datetime_display(date, timezone, 'MMMM d, yyyy')

    @app.template_filter('humanize')
    def humanize_filter(time):
        return humanize_helper(time)

    @app.template_filter('nl2br')
    def nl2br(text):
        if not text:
            return text
        return text.replace('\n', '<br/>')

    @app.template_filter('strip_tags')
    def strip(text):
        if not text:
            return text
        return strip_tags(text)
