import factory

import app.factories.common as common
from app.models.user_token_blacklist import UserTokenBlackListTime, db
from app.factories.user import UserFactory


class UserTokenBlacklistFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = UserTokenBlackListTime
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'

    user = factory.SubFactory(UserFactory)
