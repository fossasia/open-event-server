import factory

from app.models.group import Group
from tests.factories.base import BaseFactory
from tests.factories.event import EventFactoryBasic
from tests.factories.user import UserFactory


class GroupFactoryBase(BaseFactory):
    class Meta:
        model = Group

    name = 'Group'


class GroupFactory(GroupFactoryBase):
    user = factory.RelatedFactory(UserFactory)
    user_id = 1


class GroupFactoryBasic(GroupFactoryBase):
    user_id = 1
    event_id = 1


class GroupSubFactory(GroupFactoryBase):
    user = factory.SubFactory(UserFactory)
    event = factory.RelatedFactory(EventFactoryBasic)
