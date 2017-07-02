import factory
from app.models.track import db, Track
from app.factories.event import EventFactoryBasic
import app.factories.common as common


class TrackFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Track
        sqlalchemy_session = db.session

    event = factory.RelatedFactory(EventFactoryBasic)
    name = common.string_
    description = common.string_
    color = "#0f0f0f"
