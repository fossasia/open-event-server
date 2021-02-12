import factory

from app.models.group import Group
from tests.factories.base import BaseFactory
from tests.factories.user import UserFactory


class GroupFactory(BaseFactory):
    class Meta:
        model = Group

    name = 'eventgp1'
    user = factory.RelatedFactory(UserFactory)
    user_id = 1
