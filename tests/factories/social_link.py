import factory

import tests.factories.common as common
from tests.factories.event import EventFactoryBasic
from app.models.social_link import SocialLink, db


class SocialLinkFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = SocialLink
        sqlalchemy_session = db.session

    event = factory.RelatedFactory(EventFactoryBasic)
    name = common.string_
    link = common.socialUrl_('facebook')
    identifier = common.string_
    event_id = 1
