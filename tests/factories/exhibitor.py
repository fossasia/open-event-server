import factory

from app.models.exhibitor import Exhibitor
from tests.factories import common
from tests.factories.base import BaseFactory
from tests.factories.event import EventFactoryBasic


class ExhibitorFactoryBase(BaseFactory):
    class Meta:
        model = Exhibitor

    name = common.string_
    description = common.string_
    url = common.url_
    logo_url = common.imageUrl_
    banner_url = common.imageUrl_
    video_url = common.imageUrl_
    slides_url = common.imageUrl_


class ExhibitorFactory(ExhibitorFactoryBase):
    event = factory.RelatedFactory(EventFactoryBasic)
    event_id = 1


class ExhibitorSubFactory(ExhibitorFactoryBase):
    event = factory.SubFactory(EventFactoryBasic)
