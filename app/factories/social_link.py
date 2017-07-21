import factory
from app.models.social_link import db, SocialLink
from app.factories.event import EventFactoryBasic
import app.factories.common as common


class SocialLinkFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = SocialLink
        sqlalchemy_session = db.session

    event = factory.RelatedFactory(EventFactoryBasic)
    name = common.string_
    link = common.socialUrl_('facebook')
    event_id = 1
