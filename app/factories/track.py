import factory

import app.factories.common as common
from app.factories.event import EventFactoryBasic
from app.models.track import db, Track


class TrackFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Track
        sqlalchemy_session = db.session

    event = factory.RelatedFactory(EventFactoryBasic)
    event_id = 1
    name = common.string_
    description = common.string_
    color = "#0f0f0f"
