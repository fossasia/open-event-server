import factory

from app.models.sponsor import Sponsor
from tests.factories import common
from tests.factories.base import BaseFactory
from tests.factories.event import EventFactoryBasic


class SponsorFactory(BaseFactory):
    class Meta:
        model = Sponsor

    event = factory.RelatedFactory(EventFactoryBasic)
    name = common.string_
    description = common.string_
    url = common.url_
    level = 1
    logo_url = common.imageUrl_
    type = 'Gold'
    event_id = 1
