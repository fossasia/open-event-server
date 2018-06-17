import factory

import app.factories.common as common
from app.factories.event import EventFactoryBasic
from app.models import db
from app.models.stripe_authorization import StripeAuthorization


class StripeAuthorizationFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = StripeAuthorization
        sqlalchemy_session = db.session

    event = factory.RelatedFactory(EventFactoryBasic)
    stripe_secret_key = common.string_
    stripe_refresh_token = common.string_
    stripe_publishable_key = common.string_
    stripe_user_id = common.string_
    stripe_auth_code = common.secret_
    event_id = 1
