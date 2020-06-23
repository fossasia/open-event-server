from flask_rest_jsonapi.schema import get_relationships
from sqlalchemy import inspect

from app.api.helpers.errors import UnprocessableEntityError
from app.models.custom_form import CustomForms


def object_as_dict(obj):
    return {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs}


def validate_custom_form_constraints(form, obj):
    required_form_fields = CustomForms.query.filter_by(
        form=form, event_id=obj.event_id, is_included=True, is_required=True
    )
    missing_required_fields = []
    for field in required_form_fields.all():
        if not field.is_complex:
            if not getattr(obj, field.identifier):
                missing_required_fields.append(field.identifier)
        else:

            if not (obj.complex_field_values or {}).get(field.identifier):
                missing_required_fields.append(field.identifier)

    if len(missing_required_fields) > 0:
        raise UnprocessableEntityError(
            {'pointer': '/data/attributes'},
            f'Missing required fields {missing_required_fields}',
        )


def validate_custom_form_constraints_request(form, schema, obj, data):
    new_obj = type(obj)(**object_as_dict(obj))
    relationship_fields = get_relationships(schema)
    for key, value in data.items():
        if hasattr(new_obj, key) and key not in relationship_fields:
            setattr(new_obj, key, value)

    validate_custom_form_constraints(form, new_obj)
