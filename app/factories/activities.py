import factory

import app.factories.common as common
from app.models.activity import db, Activity


class ActivityFactory(factory.alchemy.SQLAlchemyModelFactory):

    class Meta:
        model = Activity
        sqlalchemy_session = db.session

    actor = common.string_
    action = common.string_
