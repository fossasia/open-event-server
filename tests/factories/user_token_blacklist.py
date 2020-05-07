import factory

from app.models.user_token_blacklist import UserTokenBlackListTime, db


class UserTokenBlacklistFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = UserTokenBlackListTime
        sqlalchemy_session = db.session

    user_id = 1
