import factory

import tests.factories.common as common
from tests.factories.event import EventFactoryBasic
from app.models.sponsor import Sponsor, db


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
