import factory

from app.models.stripe_authorization import StripeAuthorization
from tests.factories import common
from tests.factories.base import BaseFactory
from tests.factories.event import EventFactoryBasic


class StripeAuthorizationFactory(BaseFactory):
    class Meta:
        model = StripeAuthorization

    event = factory.RelatedFactory(EventFactoryBasic)
    stripe_secret_key = common.string_
    stripe_refresh_token = common.string_
    stripe_publishable_key = common.string_
    stripe_user_id = common.string_
    stripe_auth_code = common.secret_
    event_id = 1
