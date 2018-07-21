import factory

import app.factories.common as common
from app.factories.event import EventFactoryBasic
from app.models.speakers_call import db, SpeakersCall


class SpeakersCallFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = SpeakersCall
        sqlalchemy_session = db.session

    event = factory.RelatedFactory(EventFactoryBasic)
    announcement = common.string_
    starts_at = common.date_
    ends_at = common.dateEnd_
    hash = common.string_
    privacy = "public"
    event_id = 1
