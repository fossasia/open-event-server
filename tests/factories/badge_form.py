import factory

from app.models.badge_form import BadgeForms
from tests.factories import common
from tests.factories.base import BaseFactory
from tests.factories.event import EventFactoryBasic


class BadgeFormFactory(BaseFactory):
    class Meta:
        model = BadgeForms

    event = factory.RelatedFactory(EventFactoryBasic)
    event_id = 1
    badge_id = common.string_
    badge_size = common.string_
    badge_color = common.string_
    badge_image_url = common.string_
    badge_orientation = common.string_
