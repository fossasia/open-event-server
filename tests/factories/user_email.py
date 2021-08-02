import factory

from app.models.user_email import UserEmail
from tests.factories import common
from tests.factories.base import BaseFactory
from tests.factories.user import UserFactory


class UserEmailFactory(BaseFactory):
    class Meta:
        model = UserEmail

    user = factory.RelatedFactory(UserFactory)
    user_id = 1
    email_address = common.email_
    type = common.string_
