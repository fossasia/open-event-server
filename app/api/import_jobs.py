from flask_jwt_extended import current_user
from flask_rest_jsonapi import ResourceDetail, ResourceList

from app.api.helpers.permissions import jwt_required
from app.api.schema.import_jobs import ImportJobSchema
from app.models import db
from app.models.import_job import ImportJob


class ImportJobList(ResourceList):
    """
    List ImportJob
    """

    def query(self, kwargs):
        query_ = self.session.query(ImportJob)
        query_ = query_.filter_by(user_id=current_user.id)
        return query_

    decorators = (jwt_required,)
    schema = ImportJobSchema
    data_layer = {
        'session': db.session,
        'model': ImportJob,
        'methods': {
            'query': query,
        },
    }


class ImportJobDetail(ResourceDetail):
    """
    ImportJob Detail by id
    """

    decorators = (jwt_required,)
    schema = ImportJobSchema
    data_layer = {'session': db.session, 'model': ImportJob}
