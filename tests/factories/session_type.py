import factory

import tests.factories.common as common
from app.models.session_type import SessionType
from tests.factories.base import BaseFactory
from tests.factories.event import EventFactoryBasic


class SessionTypeFactory(BaseFactory):
    class Meta:
        model = SessionType

    event = factory.RelatedFactory(EventFactoryBasic)
    name = common.string_
    length = '00:30'
    event_id = 1
