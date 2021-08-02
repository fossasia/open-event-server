import factory

from app.models.social_link import SocialLink
from tests.factories import common
from tests.factories.base import BaseFactory
from tests.factories.event import EventFactoryBasic


class SocialLinkFactory(BaseFactory):
    class Meta:
        model = SocialLink

    event = factory.RelatedFactory(EventFactoryBasic)
    name = common.string_
    link = common.socialUrl_('facebook')
    identifier = common.string_
    event_id = 1
