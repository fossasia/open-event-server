from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Schema

from app.api.helpers.utilities import dasherize


class ImportJobSchema(Schema):
    """
    Api schema for ImportJob Model
    """

    class Meta:
        """
        Meta class for ImportJob Api Schema
        """

        type_ = 'import-job'
        self_view = 'v1.import_job_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    id = fields.Str(dump_only=True)
    task = fields.Str(allow_none=False)
    starts_at = fields.DateTime(required=True, timezone=True)
    result = fields.Str(allow_none=True)
    result_status = fields.Str(allow_none=True)
