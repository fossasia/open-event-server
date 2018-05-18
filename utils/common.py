from marshmallow import pre_load

from app.api.helpers.utilities import dasherize


def patch_defaults(schema, in_data):
    """
    Add default values to None fields
    :param schema: Schema
    :param in_data: the json data comprising of the fields
    :return: json data with default values
    """
    for name, field in schema.fields.items():
        dasherized_name = dasherize(name)
        attribute = in_data.get(dasherized_name)
        if attribute is None:
            in_data[dasherized_name] = field.default
    return in_data


@pre_load
def make_object(schema, in_data):
    """
    Returns the json data after adding defaults
    :param schema: Schema
    :param in_data: the json data comprising of the fields
    :return: json data returned by the patch_default function
    """
    return patch_defaults(schema, in_data)


def use_defaults():
    """
    Decorator added to model classes which have default values specified for one of it's fields
    Adds the make_object method defined above to the class.
    :return: wrapper
    """
    def wrapper(k, *args, **kwargs):
        setattr(k, "make_object", eval("make_object", *args, **kwargs))
        return k
    return wrapper
