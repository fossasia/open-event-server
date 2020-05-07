import factory

import tests.factories.common as common
from app.models.speakers_call import SpeakersCall
from tests.factories.base import BaseFactory
from tests.factories.event import EventFactoryBasic


class SpeakersCallFactory(BaseFactory):
    class Meta:
        model = SpeakersCall

    event = factory.RelatedFactory(EventFactoryBasic)
    announcement = common.string_
    starts_at = common.date_
    ends_at = common.dateEnd_
    hash = common.string_
    privacy = "public"
    event_id = 1
