import unittest
#improting datetime
from datetime import datetime

#importing routes
from app.api import routes

from unittest import TestCase
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

class TestCreatedatValidation(TestCase):

    def test_createdat_all_models(self):
        '''
            createdat validate time : Tests created_at variable in all models 
        '''
        #all the models having created_at are stored in a set 
        created_at_models=[Session, User, Event , AccessCode, Order, Session, TicketHolder, RoleInvite, DiscountCode, UserTokenBlackListTime, EventInvoice]
        for model in created_at_models:
            #looping through each model in a subtest to check if created_at time is set to current time
            with self.subTest(model=model):
                self.assertEqual(model.created_at,datetime.now(),'\nTests created_at in module {}'.format(model))
            
if __name__ == "__main__":
    unittest.main()
