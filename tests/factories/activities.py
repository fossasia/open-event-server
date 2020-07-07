from app.models.activity import Activity
from tests.factories import common as common
from tests.factories.base import BaseFactory


class ActivityFactory(BaseFactory):
    class Meta:
        model = Activity

    actor = common.string_
    action = common.string_
