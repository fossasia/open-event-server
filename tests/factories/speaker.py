import factory

from app.models.speaker import Speaker
from tests.factories import common
from tests.factories.base import BaseFactory
from tests.factories.event import EventFactoryBasic
from tests.factories.session import SessionFactory
from tests.factories.user import UserFactory


class SpeakerFactoryBase(BaseFactory):
    class Meta:
        model = Speaker

    name = common.string_
    email = common.email_
    photo_url = common.url_
    thumbnail_image_url = common.url_
    small_image_url = common.url_
    icon_image_url = common.url_
    short_biography = common.string_
    long_biography = common.string_
    speaking_experience = common.string_
    mobile = common.string_
    website = common.url_
    twitter = common.url_
    facebook = common.url_
    github = common.url_
    linkedin = common.url_
    organisation = common.string_
    is_featured = False
    position = common.string_
    country = common.string_
    city = common.string_
    gender = common.string_
    heard_from = common.string_
    sponsorship_required = common.string_


class SpeakerFactory(SpeakerFactoryBase):
    event = factory.RelatedFactory(EventFactoryBasic)
    user = factory.RelatedFactory(UserFactory)
    session = factory.RelatedFactory(SessionFactory)
    event_id = 1
    user_id = 2


class SpeakerSubFactory(SpeakerFactoryBase):
    event = factory.SubFactory(EventFactoryBasic)
    user = factory.SubFactory(UserFactory)
