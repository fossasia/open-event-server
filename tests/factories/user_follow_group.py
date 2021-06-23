import factory

from app.models.user import User
from app.models.user_follow_group import UserFollowGroup
from tests.factories.base import BaseFactory
from tests.factories.group import GroupFactoryBasic


class UserFollowGroupFactory(BaseFactory):
    class Meta:
        model = UserFollowGroup

    user = factory.LazyAttribute(lambda a: User.query.first())
    group = factory.SubFactory(GroupFactoryBasic)
