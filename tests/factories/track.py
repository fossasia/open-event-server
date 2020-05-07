import factory

import tests.factories.common as common
from app.models.track import Track
from tests.factories.base import BaseFactory
from tests.factories.event import EventFactoryBasic


class TrackFactory(BaseFactory):
    class Meta:
        model = Track

    event = factory.RelatedFactory(EventFactoryBasic)
    event_id = 1
    name = common.string_
    description = common.string_
    color = "#0f0f0f"
