from app.models.service import Service
from tests.factories import common as common
from tests.factories.base import BaseFactory


class ServiceFactory(BaseFactory):
    class Meta:
        model = Service

    name = common.string_
