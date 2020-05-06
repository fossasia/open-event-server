def extract_from_marshmallow(schema_class):
    return schema_class._declared_fields.keys()
