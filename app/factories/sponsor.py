import factory

import app.factories.common as common
from app.factories.event import EventFactoryBasic
from app.models.sponsor import db, Sponsor


class SponsorFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Sponsor
        sqlalchemy_session = db.session

    event = factory.RelatedFactory(EventFactoryBasic)
    name = common.string_
    description = common.string_
    url = common.url_
    level = 1
    logo_url = common.imageUrl_
    type = 'Gold'
    event_id = 1
