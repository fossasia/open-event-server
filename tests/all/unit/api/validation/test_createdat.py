import unittest
from datetime import datetime, timedelta, timezone
from app.factories.session import SessionFactory
from app.factories.user import UserFactory
from app.factories.event import EventFactoryBasic
from app.factories.access_code import AccessCodeFactory
from app.factories.event_invoice import EventInvoiceFactory
from app.factories.ticket_holder import TicketHolderFactory
from app.factories.discount_code import DiscountCodeFactory
from app.factories.order import OrderFactory
from app.factories.role_invite import RoleInviteFactory
from app.factories.user_token_blacklist import UserTokenBlacklistFactory
from tests.all.integration.utils import OpenEventTestCase


class TestCreatedatValidation(OpenEventTestCase):
    def test_createdat(self):
        """ Validate time : Tests if created_at is set to current time in all models
        """
        with self.app.test_request_context():
            model_factories = [
                UserFactory,
                EventInvoiceFactory,
                AccessCodeFactory,
                EventFactoryBasic,
                OrderFactory,
                RoleInviteFactory,
                DiscountCodeFactory,
                TicketHolderFactory,
                SessionFactory,
                UserTokenBlacklistFactory,
            ]
            models_with_utcnow = [
                TicketHolderFactory,
                DiscountCodeFactory,
                EventInvoiceFactory,
            ]
            for model_factory in model_factories:
                with self.subTest(model_factory=model_factory):
                    test_model = model_factory()
                    if model_factory in models_with_utcnow:
                        current_time = datetime.utcnow().astimezone()
                    else:
                        current_time = datetime.now(timezone.utc).astimezone()
                    createdat_db = test_model.created_at
                    time_diff = current_time - createdat_db
                    allowed_time_lag = timedelta(milliseconds=500)
                    message = "created_at not set" " to current time in {} \n".format(
                        model_factory
                    )
                    self.assertLessEqual(time_diff, allowed_time_lag, message)


if __name__ == "__main__":
    unittest.main()
