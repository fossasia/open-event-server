import factory

from app.models.custom_form import CustomForms
from tests.factories.base import BaseFactory
from tests.factories.event import EventFactoryBasic


class CustomFormFactory(BaseFactory):
    class Meta:
        model = CustomForms

    event = factory.RelatedFactory(EventFactoryBasic)
    form = 'attendee'
    name = 'First Name'
    field_identifier = 'firstname'
    type = "text"
    is_required = False
    is_included = False
    is_fixed = False
    event_id = 1
