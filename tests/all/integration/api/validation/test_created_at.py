import unittest
from datetime import datetime, timedelta, timezone

from app.models import db
from tests.all.integration.utils import OpenEventLegacyTestCase
from tests.factories.access_code import AccessCodeFactory
from tests.factories.attendee import AttendeeFactory
from tests.factories.discount_code import DiscountCodeFactory
from tests.factories.event import EventFactoryBasic
from tests.factories.event_invoice import EventInvoiceFactory
from tests.factories.order import OrderFactory
from tests.factories.role_invite import RoleInviteFactory
from tests.factories.session import SessionFactory
from tests.factories.user import UserFactory
from tests.factories.user_token_blacklist import UserTokenBlacklistFactory
from tests.factories.video_channel import VideoChannelFactory


class TestCreatedAtValidation(OpenEventLegacyTestCase):
    def test_created_at(self):
        """Validate time : Tests if created_at is set to current time in all models"""
        with self.app.test_request_context():
            model_factories = [
                UserFactory,
                EventInvoiceFactory,
                AccessCodeFactory,
                EventFactoryBasic,
                OrderFactory,
                RoleInviteFactory,
                DiscountCodeFactory,
                AttendeeFactory,
                SessionFactory,
                UserTokenBlacklistFactory,
            ]
            models_with_utcnow = [
                AttendeeFactory,
                DiscountCodeFactory,
                EventInvoiceFactory,
                VideoChannelFactory,
            ]
            for model_factory in model_factories:
                with self.subTest(model_factory=model_factory):
                    test_model = model_factory()
                    db.session.commit()
                    if model_factory in models_with_utcnow:
                        current_time = datetime.utcnow().astimezone()
                    else:
                        current_time = datetime.now(timezone.utc).astimezone()
                    created_at_db = test_model.created_at
                    assert created_at_db is not None, 'created_at None for ' + str(
                        model_factory
                    )
                    time_diff = current_time - created_at_db
                    allowed_time_lag = timedelta(milliseconds=400)
                    message = "created_at not set" " to current time in {} \n".format(
                        model_factory
                    )
                    assert time_diff <= allowed_time_lag, message


if __name__ == "__main__":
    unittest.main()
