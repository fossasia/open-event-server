from app.api.helpers.errors import UnprocessableEntityError
from app.settings import get_settings


def validate_complex_fields_json(self, data, original_data):
    if data.get('complex_field_values'):
        if any(
            ((not isinstance(i, (str, bool, int, float))) and i is not None)
            for i in data['complex_field_values'].values()
        ):
            raise UnprocessableEntityError(
                {'pointer': '/data/attributes/complex_field_values'},
                "Only flattened JSON of form {key: value} where value is a string, "
                "integer, float, bool or null is permitted for this field",
            )

        if (
            len(data['complex_field_values'])
            > get_settings()['max_complex_custom_fields']
        ):
            raise UnprocessableEntityError(
                {'pointer': '/data/attributes/complex_field_values'},
                "A maximum of {} complex custom form fields are currently supported".format(
                    get_settings()['max_complex_custom_fields']
                ),
            )
