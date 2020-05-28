from app.models.module import Module
from tests.factories.base import BaseFactory


class ModuleFactory(BaseFactory):
    class Meta:
        model = Module

    donation_include = True
    ticket_include = True
    payment_include = True
