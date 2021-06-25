import datetime

import pytz

from app.templates.flask_ext.jinja.filters import humanize_helper
from tests.factories.order import OrderFactory


def test_humanize_helper(db):
    """Method to test humanization of order creation time"""

    test_order = OrderFactory(
        created_at=datetime.datetime.now(pytz.utc) - datetime.timedelta(days=10)
    )
    actual_response = humanize_helper(test_order.created_at)
    expected_response = '10 days ago'
    assert actual_response == expected_response

    actual_response = humanize_helper(test_order.completed_at)
    expected_response = 'N/A'
    assert actual_response == expected_response
