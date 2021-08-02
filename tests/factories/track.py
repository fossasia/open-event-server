import factory

from app.models.track import Track
from tests.factories import common
from tests.factories.base import BaseFactory
from tests.factories.event import EventFactoryBasic


class TrackFactoryBase(BaseFactory):
    class Meta:
        model = Track

    name = common.string_
    description = common.string_
    color = "#0f0f0f"


class TrackSubFactory(TrackFactoryBase):
    event = factory.SubFactory(EventFactoryBasic)


class TrackFactory(TrackFactoryBase):
    event = factory.RelatedFactory(EventFactoryBasic)
    event_id = 1
