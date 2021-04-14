import factory

from app.models.group import Group
from tests.factories.base import BaseFactory
from tests.factories.user import UserFactory


class GroupFactoryBase(BaseFactory):
    class Meta:
        model = Group

    name = 'Group'


class GroupFactory(GroupFactoryBase):
    user = factory.RelatedFactory(UserFactory)
    user_id = 1


class GroupSubFactory(GroupFactoryBase):
    user = factory.SubFactory(UserFactory)
