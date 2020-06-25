from marshmallow import fields

from app.api.helpers.utilities import dict_to_snake_case


class CustomFormValueField(fields.Dict):
    def _deserialize(self, value, attr, data):
        deserialized = super()._deserialize(value, attr, data)

        return dict_to_snake_case(deserialized)
