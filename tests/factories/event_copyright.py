import factory

from app.models.event_copyright import EventCopyright
from tests.factories import common
from tests.factories.base import BaseFactory
from tests.factories.event import EventFactoryBasic


class EventCopyrightFactory(BaseFactory):
    class Meta:
        model = EventCopyright

    event = factory.RelatedFactory(EventFactoryBasic)
    holder = common.string_
    holder_url = common.url_
    licence = common.string_
    licence_url = common.url_
    year = 2007
    logo = common.url_
    event_id = 1
