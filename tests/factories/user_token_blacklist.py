from app.models.user_token_blacklist import UserTokenBlackListTime
from tests.factories.base import BaseFactory


class UserTokenBlacklistFactory(BaseFactory):
    class Meta:
        model = UserTokenBlackListTime

    user_id = 1
