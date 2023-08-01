import marshmallow
from flask_rest_jsonapi.schema import get_relationships
from sqlalchemy import inspect

from app.api.helpers.errors import UnprocessableEntityError
from app.api.schema.base import TrimmedEmail
from app.models.custom_form import CustomForms
from app.models.ticket import Ticket


def object_as_dict(obj):
    return {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs}


def get_schema(form_fields):
    attrs = {}

    for field in form_fields:
        if field.type in [
            'text',
            'checkbox',
            'select',
            'paragraph',
            'year',
            'richtextlink',
        ]:
            field_type = marshmallow.fields.Str
        elif field.type == 'email':
            field_type = TrimmedEmail
        elif field.type == 'number':
            field_type = marshmallow.fields.Float
        elif field.type == 'boolean':
            field_type = marshmallow.fields.Str
        else:
            raise UnprocessableEntityError(
                {'pointer': '/data/complex-field-values/' + field.identifier},
                'Invalid Field Type: ' + field.type,
            )
        attrs[field.identifier] = field_type(required=field.is_required)
    return type('DynamicSchema', (marshmallow.Schema,), attrs)


def validate_custom_form_constraints(form, obj, excluded):
    """
    The validate custom form constraints.
    """
    conditions = {
        'form': form,
        'event_id': obj.event_id,
        'is_included': True,
    }
    if hasattr(obj, 'ticket_id'):
        ticket = Ticket.query.filter_by(id=obj.ticket_id).first()
        conditions.update({'form_id': ticket.form_id})
    form_fields = CustomForms.query.filter_by(**conditions).all()
    required_form_fields = filter(lambda field: field.is_required, form_fields)
    missing_required_fields = []
    for field in required_form_fields:
        if field.identifier in excluded:
            continue
        if not field.is_complex:
            if not getattr(obj, field.identifier):
                missing_required_fields.append(field.name)
        else:
            if obj.complex_field_values:
                if obj.complex_field_values.get(field.identifier) is None:
                    missing_required_fields.append(field.name)
            else:
                missing_required_fields.append(field.name)

    if len(missing_required_fields) > 0:
        raise UnprocessableEntityError(
            {'pointer': '/data/attributes'},
            f'Missing required fields {missing_required_fields}',
        )

    if obj.complex_field_values:
        complex_form_fields = filter(lambda field: field.is_complex, form_fields)
        schema = get_schema(complex_form_fields)()

        data, errors = schema.load(obj.complex_field_values)

        if errors:
            raise UnprocessableEntityError({'errors': errors}, 'Schema Validation Error')

        # We need to save null if resultant dictionary is empty
        return data if data else None


def validate_custom_form_constraints_request(form, schema, obj, data, excluded=None):
    """
    The validate custom form constraints request.
    """
    if excluded is None:
        excluded = []
    new_obj = type(obj)(**object_as_dict(obj))
    relationship_fields = get_relationships(schema)
    for key, value in data.items():
        if hasattr(new_obj, key) and key not in relationship_fields:
            setattr(new_obj, key, value)

    return validate_custom_form_constraints(
        form, new_obj, set(relationship_fields.keys()) | set(excluded)
    )
