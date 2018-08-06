import factory

import app.factories.common as common
from app.factories.user import UserFactory
from app.models.user_email import db, UserEmail


class UserEmailFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = UserEmail
        sqlalchemy_session = db.session

    user = factory.RelatedFactory(UserFactory)
    user_id = 1
    email_address = common.email_
    type = common.string_
