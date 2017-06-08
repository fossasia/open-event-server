from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from marshmallow_jsonapi.flask import Schema, Relationship
from marshmallow_jsonapi import fields

from app.models import db
from app.models.import_job import ImportJob
from app.models.user import User
from app.api.helpers.permissions import jwt_required, is_user_itself


class ImportJobSchema(Schema):
    """
    Api schema for import_jobs model
    """
    class Meta:
        """
        Meta class for ImportJob Api Schema
        """
        type_ = 'import_job'
        self_view = 'v1.import_job_detail'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'v1.import_job_list'

    id = fields.Str(dump_only=True)
    task = fields.Str(required=True)
    starts_at = fields.DateTime()
    result = fields.Str()
    result_status = fields.Str()
    user = Relationship(
        attribute='user',
        self_view='v1.import_job_user',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.user_detail',
        related_view_kwargs={'import_job_id': '<id>'},
        schema='UserSchema',
        type_='user')


class ImportJobList(ResourceList):
    """
    List all the ImportJob
    """
    def query(self, view_kwargs):
        query_ = self.session.query(ImportJob)
        if view_kwargs.get('user_id') is not None:
            query_ = query_.join(User).filter(User.id == view_kwargs['user_id'])
        return query_

    def before_create_object(self, data, view_kwargs):
        if view_kwargs.get('user_id') is not None:
            user = self.session.query(User).filter_by(id=view_kwargs['user_id']).one()
            data['user_id'] = user.id

    view_kwargs = True
    get = is_user_itself(ResourceList.get.__func__)
    post = jwt_required(ResourceList.post.__func__)
    schema = ImportJobSchema
    data_layer = {'session': db.session,
                  'model': ImportJob,
                  'methods': {
                      'query': query,
                      'before_create_object': before_create_object
                  }}


class ImportJobDetail(ResourceDetail):
    """
    ImportJob detail by ID
    """
    decorators = (is_user_itself, )
    schema = ImportJobSchema
    data_layer = {'session': db.session,
                  'model': ImportJob}


class ImportJobRelationship(ResourceRelationship):
    decorators = (is_user_itself, )
    schema = ImportJobSchema
    data_layer = {'session': db.session,
                  'model': ImportJob}
