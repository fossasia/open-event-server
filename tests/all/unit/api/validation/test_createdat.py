import unittest
from datetime import datetime, timedelta, timezone

from app.api.helpers.db import save_to_db
from app.models import db
from app.models.access_code import AccessCode
from app.models.discount_code import DiscountCode
from app.models.event import Event
from app.models.event_invoice import EventInvoice
from app.models.order import Order
from app.models.role_invite import RoleInvite
from app.models.session import Session
from app.models.ticket_holder import TicketHolder
from app.models.user import User
from tests.all.integration.utils import OpenEventTestCase


class TestCreatedatValidation(OpenEventTestCase):
    def test_createdat(self):
        """ Validate time : Tests if created_at is set to current time in all models
        """
        with self.app.test_request_context():
            test_user = User(email='authtest@gmail.com', password='password')
            test_event = Event(
                name='test event',
                starts_at=datetime.now(),
                ends_at=datetime.now() + timedelta(days=1),
                logo_url='foo.com',
            )
            test_session = Session(title='Test Session')
            test_access_code = AccessCode(code=123)
            test_order = Order()
            test_ticket_holder = TicketHolder(firstname="John", lastname="Snow")
            test_role_invite = RoleInvite(email="testrole@mail.com", role_name="Nothing")
            test_discount_code = DiscountCode(
                code="123", value=0.0, type="test", used_for="nothing"
            )
            test_event_invoice = EventInvoice()
            test_models = [
                test_user,
                test_event,
                test_access_code,
                test_order,
                test_ticket_holder,
                test_role_invite,
                test_discount_code,
                test_session,
                test_event_invoice,
            ]
            model_classes = [
                User,
                Event,
                AccessCode,
                Order,
                TicketHolder,
                RoleInvite,
                DiscountCode,
                Session,
                EventInvoice,
            ]
            test_models_with_utcnow = [
                test_ticket_holder,
                test_discount_code,
                test_event_invoice,
            ]
            allowed_time_lag = timedelta(milliseconds=300)
            for model, model_class in zip(test_models, model_classes):
                with self.subTest(model=model, model_class=model_class):
                    save_to_db(model)
                    model_id = model.id
                    model_createdat = (
                        db.session.query(model_class).get(model_id).created_at
                    )
                    db.session.delete(model)
                    db.session.commit()
                    if model in test_models_with_utcnow:
                        current_time = datetime.utcnow().astimezone()
                    else:
                        current_time = datetime.now(timezone.utc)
                    time_diff = current_time - model_createdat
                    message = "created_at not set" " to current time in {} \n".format(
                        model
                    )
                    self.assertLessEqual(time_diff, allowed_time_lag, message)


if __name__ == "__main__":
    unittest.main()
