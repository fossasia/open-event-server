from flask_rest_jsonapi import ResourceList, ResourceDetail

from app.api.schema.import_jobs import ImportJobSchema
from app.models import db
from app.models.import_job import ImportJob
from app.api.helpers.permissions import jwt_required
from flask_jwt import current_identity


class ImportJobList(ResourceList):
    """
    List ImportJob
    """
    def query(self, kwargs):
        query_ = self.session.query(ImportJob)
        query_ = query_.filter_by(user_id=current_identity.id)
        return query_

    decorators = (jwt_required,)
    schema = ImportJobSchema
    data_layer = {'session': db.session,
                  'model': ImportJob,
                  'methods': {
                      'query': query,
                  }}


class ImportJobDetail(ResourceDetail):
    """
    ImportJob Detail by id
    """
    decorators = (jwt_required, )
    schema = ImportJobSchema
    data_layer = {'session': db.session,
                  'model': ImportJob}
