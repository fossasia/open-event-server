from flask_rest_jsonapi import ResourceDetail, ResourceList

from flask_jwt import current_identity as current_user
from app.api.schema.import_jobs import ImportJobSchema
from app.models import db
from app.api.helpers.db import safe_query
from app.models.import_job import ImportJob
from app.models.user import User
from app.api.helpers.permissions import jwt_required
from app.api.helpers.permission_manager import has_access


class ImportJobList(ResourceList):
    """
    List ImportJob
    """
    def query(self, view_kwargs):
        query_ = self.session.query(ImportJob)
        user_id = current_user.id
        user = safe_query(self, User, 'id', user_id, 'user_id')
        if not has_access('is_user_itself', user_id=user.id):
            raise ForbiddenException({'source': ''}, 'Access Forbidden')
        query_ = query_.join(User, User.id == ImportJob.user_id).filter(User.id == user.id)
        return query_

    decorators = (jwt_required,)
    schema = ImportJobSchema
    data_layer = {'session': db.session,
                  'model': ImportJob,
                  'methods': {
                      'query': query
                  }}
