import factory

from app.models.badge_field_form import BadgeFieldForms
from tests.factories import common
from tests.factories.badge_form import BadgeFormFactory
from tests.factories.base import BaseFactory


class BadgeFieldFormFactory(BaseFactory):
    class Meta:
        model = BadgeFieldForms

    badge_form = factory.RelatedFactory(BadgeFormFactory)
    badge_form_id = 1
    badge_id = common.string_
    field_identifier = common.string_
    custom_field = common.string_
    sample_text = common.string_
    font_size = common.int_
    font_name = common.string_
    font_weight = common.int_
    font_color = common.string_
    text_rotation = common.int_
    text_alignment = common.string_
    text_type = common.string_
    is_deleted = common.boolean_
    margin_top = common.int_
    margin_bottom = common.int_
    margin_left = common.int_
    margin_right = common.int_
    qr_custom_field = common.array_
