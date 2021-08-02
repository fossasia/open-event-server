from app.models.custom_placeholder import CustomPlaceholder
from tests.factories import common
from tests.factories.base import BaseFactory


class CustomPlaceholderFactory(BaseFactory):
    class Meta:
        model = CustomPlaceholder

    name = common.string_
    origin = common.string_
    copyright = common.string_
    original_image_url = common.imageUrl_
    event_sub_topic_id = None
