from marshmallow import Schema, ValidationError, fields, validate, validates_schema

CHECK_IN_TYPE = ['event', 'virtual-room', 'room']


class VirtualCheckInSchema(Schema):
    id = fields.Integer(dump_only=True)
    check_in_type = fields.Str(
        nullable=False, required=True, validate=validate.OneOf(choices=CHECK_IN_TYPE)
    )
    microlocation_id = fields.Integer(nullable=True)
    is_check_in = fields.Boolean(required=True, nullable=False)
    check_in_at = fields.DateTime(dump_only=True)
    check_out_at = fields.DateTime(dump_only=True)

    @validates_schema
    def validate_microlocation_requires_a(self, data):
        """
        validate when check_in_type is room, microlocation id is required
        @param data: data
        """
        if (
            'check_in_type' in data
            and data['check_in_type'] == 'room'
            and 'microlocation_id' not in data
        ):
            raise ValidationError('microlocation_id is required for room check in.')
