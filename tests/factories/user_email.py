import factory

import tests.factories.common as common
from tests.factories.user import UserFactory
from app.models.user_email import UserEmail, db


class UserEmailFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = UserEmail
        sqlalchemy_session = db.session

    user = factory.RelatedFactory(UserFactory)
    user_id = 1
    email_address = common.email_
    type = common.string_
