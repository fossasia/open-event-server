import factory

from app.models.speakers_call import SpeakersCall
from tests.factories import common
from tests.factories.base import BaseFactory
from tests.factories.event import EventFactoryBasic


class SpeakersCallFactoryBase(BaseFactory):
    class Meta:
        model = SpeakersCall

    announcement = common.string_
    starts_at = common.date_
    ends_at = common.dateEnd_
    hash = common.string_
    privacy = "public"


class SpeakersCallSubFactory(SpeakersCallFactoryBase):
    event = factory.SubFactory(EventFactoryBasic)


class SpeakersCallFactory(SpeakersCallFactoryBase):
    event = factory.RelatedFactory(EventFactoryBasic)
    event_id = 1
