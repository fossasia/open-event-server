import unittest

from app.models import db
from tests.all.integration.utils import OpenEventTestCase
from app.api.helpers.db import save_to_db
from datetime import datetime,  timedelta
#importing all models containing createdat variable
from app.models.user import User
from app.models.event import Event
from app.models.access_code import AccessCode
from app.models.order import Order
from app.models.session import Session
from app.models.ticket_holder import TicketHolder
from app.models.role_invite import RoleInvite
from app.models.discount_code import DiscountCode
from app.models.user_token_blacklist import UserTokenBlackListTime
from app.models.event_invoice import EventInvoice

class TestCreatedatValidation(OpenEventTestCase):

    def test_createdat_in_user(self):
        """ Created at validate time : Tests if created_at is set  
            to current time in User model
        """
        with self.app.test_request_context():
            test_user = User(email = 'authtest@gmail.com', password = 'password')
            save_to_db(test_user, "User created")
            user_id = test_user.id
            db_created_at = db.session.query(User).get(user_id).created_at
            current_time = datetime.utcnow().astimezone()
            time_diff = current_time - db_created_at
            allowed_time_lag = timedelta(milliseconds=50)
            self.assertLessEqual(time_diff, allowed_time_lag, 
                 "User model created_at not set to current time")

    def test_createdat_in_event(self):
        """ Created at validate time : Tests if created_at is set 
                to current time in Event model
        """
        with self.app.test_request_context():
            test_event = Event(name = 'test event',
                                    starts_at = datetime.now(),
                                    ends_at = datetime.now()+timedelta(days = 1),
                                    logo_url = 'foo.com')
            save_to_db(test_event)
            event_id = test_event.id
            db_created_at = db.session.query(Event).get(event_id).created_at
            current_time = datetime.utcnow().astimezone()
            time_diff = current_time - db_created_at
            allowed_time_lag = timedelta(milliseconds = 50)
            self.assertLessEqual(time_diff, allowed_time_lag, 
                "Event model created_at not set to current time")
 
    def test_createdat_in_session(self):
        """ Created at validate time : Tests if created_at is set 
            to current time in Session model
        """
        with self.app.test_request_context():
            test_session = Session(title = "Test Session")
            save_to_db(test_session)
            session_id = test_session.id
            db_created_at = db.session.query(Session).get(session_id).created_at
            current_time = datetime.utcnow().astimezone()
            time_diff = current_time - db_created_at
            allowed_time_lag = timedelta(milliseconds = 50)
            self.assertLessEqual(time_diff, allowed_time_lag, 
                "Session model created_at not set to current time")
 
    def test_createdat_in_access_code(self):
        """ Created at validate time : Tests if created_at is set 
                to current time in AccessCode model
        """
        with self.app.test_request_context(): 
            test_access_code = AccessCode(code = 123)
            save_to_db(test_access_code)
            access_code_id = test_access_code.id
            db_created_at = db.session.query(AccessCode).get(access_code_id).created_at
            current_time = datetime.utcnow().astimezone()
            time_diff = current_time - db_created_at
            allowed_time_lag = timedelta(milliseconds = 50)
            self.assertLessEqual(time_diff, allowed_time_lag, 
                "AccessCode model created_at not set to current time")
 
    def test_createdat_in_order(self):
        """ Created at validate time : Tests if created_at is set 
            to current time in Order model
        """
        with self.app.test_request_context():
            test_order = Order()
            save_to_db(test_order)
            order_id = test_order.id
            db_created_at = db.session.query(Order).get(order_id).created_at
            current_time = datetime.utcnow().astimezone()
            time_diff = current_time - db_created_at
            allowed_time_lag = timedelta(milliseconds = 50)
            self.assertLessEqual(time_diff, allowed_time_lag, 
                "Order model created_at not set to current time")

    def test_createdat_in_ticket_holder(self):
        """ Created at validate time : Tests if created_at is set 
            to current time in TickerHolder model
        """
        with self.app.test_request_context():
            test_ticket_holder = TicketHolder(firstname = "John", lastname = "Snow")
            save_to_db(test_ticket_holder)
            ticket_holder_id = test_ticket_holder.id
            db_created_at = db.session.query(TicketHolder).get(ticket_holder_id).created_at
            current_time = datetime.utcnow().astimezone()
            time_diff = current_time - db_created_at
            allowed_time_lag = timedelta(milliseconds = 50)
            self.assertLessEqual(time_diff, allowed_time_lag, 
                "TicketHolder model created_at not set to current time")
 
    def test_createdat_in_role_invite(self):
        """ Created at validate time : Tests if created_at is set 
            to current time in RoleInvite model
        """
        with self.app.test_request_context():
            test_role_invite = RoleInvite(email = "testrole@mail.com", role_name = "Nothing")
            save_to_db(test_role_invite)
            role_invite_id = test_role_invite.id
            db_created_at = db.session.query(RoleInvite).get(role_invite_id).created_at
            current_time = datetime.utcnow().astimezone()
            time_diff = current_time - db_created_at
            allowed_time_lag = timedelta(milliseconds = 50)
            self.assertLessEqual(time_diff, allowed_time_lag, 
                "RoleInvite model created_at not set to current time")
 
    def test_createdat_in_discount_code(self):
        """ Created at validate time : Tests if created_at is set 
            to current time in DiscountCode model
        """
        with self.app.test_request_context():
            test_discount_code = DiscountCode(code = "123", value = 0.0, type = "test", used_for = "nothing")
            save_to_db(test_discount_code)
            discount_code_id = test_discount_code.id
            db_created_at = db.session.query(DiscountCode).get(discount_code_id).created_at
            current_time = datetime.utcnow().astimezone()
            time_diff = current_time - db_created_at
            allowed_time_lag = timedelta(milliseconds = 50)
            self.assertLessEqual(time_diff, allowed_time_lag, 
                "DiscountCode model created_at not set to current time")

    def test_createdat_in_user_token_blacklist(self):
        """ Created at validate time : Tests if created_at is set 
            to current time in UserTokenBlackListTime model
        """
        with self.app.test_request_context():
            test_user = User(email = 'authtest@gmail.com', password = 'password')
            save_to_db(test_user, "User created")
            test_user_token_blacklist = UserTokenBlackListTime(user_id = test_user.id)
            save_to_db(test_user_token_blacklist)
            user_token_blacklist_id = test_user_token_blacklist.id
            db_created_at = db.session.query(UserTokenBlackListTime).get(user_token_blacklist_id).created_at
            current_time = datetime.utcnow().astimezone()
            time_diff= current_time - db_created_at
            allowed_time_lag = timedelta(milliseconds = 50)
            self.assertLessEqual(time_diff, allowed_time_lag, 
                "UserTokenBlackListTime model created_at not set to current time")

    def test_createdat_in_event_invoice(self):
        """ Created at validate time : Tests if created_at is set 
            to current time in EventInvoice model
        """ 
        with self.app.test_request_context():
            test_event_invoice = EventInvoice()
            save_to_db(test_event_invoice)
            event_invoice_id = test_event_invoice.id
            db_created_at = db.session.query(EventInvoice).get(event_invoice_id).created_at
            current_time = datetime.utcnow().astimezone()
            time_diff = current_time - db_created_at
            allowed_time_lag = timedelta(milliseconds = 50)
            self.assertLessEqual(time_diff, allowed_time_lag, 
                "EventInvoice model created_at not set to current time")


if __name__ == "__main__":
    unittest.main()
