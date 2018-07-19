import factory

import app.factories.common as common
from app.factories.event import EventFactoryBasic
from app.factories.session import SessionFactory
from app.factories.user import UserFactory
from app.models.speaker import db, Speaker


class SpeakerFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Speaker
        sqlalchemy_session = db.session

    event = factory.RelatedFactory(EventFactoryBasic)
    user = factory.RelatedFactory(UserFactory)
    session = factory.RelatedFactory(SessionFactory)
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
    event_id = 1
    user_id = 2
