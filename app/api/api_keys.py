from datetime import datetime

from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from flask_rest_jsonapi.exceptions import ObjectNotFound

from app.api.helpers.db import safe_query_kwargs
from app.api.helpers.errors import ForbiddenError, UnprocessableEntityError
from app.api.helpers.permission_manager import has_access, jwt_required
from app.api.helpers.utilities import require_relationship
from app.api.schema.api_keys import ApiKeySchema
from app.models import db
from app.models.api_key import ApiKey
from app.models.user import User


class ApiKeyListPost(ResourceList):
    """
    Create API keys
    """

    def before_post(self, args, kwargs, data):
        require_relationship(['user'], data)
        if not has_access('is_user_itself', user_id=data['user']):
            raise ForbiddenError({'source': ''}, 'Access Forbidden')

    def before_create_object(self, data, view_kwargs):
        raw_token = ApiKey.generate_token()
        data['token_hash'] = ApiKey.hash_token(raw_token)
        data['prefix'] = raw_token[:8]
        self._raw_token = raw_token

    def after_create_object(self, api_key, data, view_kwargs):
        api_key.token = self._raw_token

    methods = ['POST']
    decorators = (jwt_required,)
    schema = ApiKeySchema
    data_layer = {
        'session': db.session,
        'model': ApiKey,
        'methods': {
            'before_create_object': before_create_object,
            'after_create_object': after_create_object,
        },
    }


class ApiKeyList(ResourceList):
    """
    List API keys
    """

    def query(self, view_kwargs):
        query_ = self.session.query(ApiKey)
        if view_kwargs.get('user_id'):
            user = safe_query_kwargs(User, view_kwargs, 'user_id')
            if not has_access('is_user_itself', user_id=user.id):
                raise ForbiddenError({'source': ''}, 'Access Forbidden')
            query_ = query_.filter_by(user_id=user.id)
        else:
            if not has_access('is_admin'):
                raise ForbiddenError({'source': ''}, 'Admin access is required')
        return query_

    view_kwargs = True
    methods = ['GET']
    decorators = (jwt_required,)
    schema = ApiKeySchema
    data_layer = {
        'session': db.session,
        'model': ApiKey,
        'methods': {'query': query},
    }


class ApiKeyDetail(ResourceDetail):
    """
    API key detail by id
    """

    def before_get(self, args, kwargs):
        api_key = self.session.query(ApiKey).filter_by(id=kwargs.get('id')).first()
        if not api_key:
            raise ObjectNotFound({'parameter': '{id}'}, 'API key not found')
        if not has_access('is_user_itself', user_id=api_key.user_id):
            raise ForbiddenError({'source': ''}, 'Access Forbidden')

    def before_update_object(self, api_key, data, view_kwargs):
        if not has_access('is_user_itself', user_id=api_key.user_id):
            raise ForbiddenError({'source': ''}, 'Access Forbidden')

        if data.get('token_hash') or data.get('prefix') or data.get('user'):
            raise UnprocessableEntityError(
                {'source': ''}, 'API key fields cannot be updated'
            )

        if 'revoked_at' in data and not data['revoked_at']:
            raise UnprocessableEntityError(
                {'source': ''}, 'API key revoke time cannot be cleared'
            )

        if data.get('revoked_at') and not api_key.revoked_at:
            api_key.revoked_at = data['revoked_at']
        elif data.get('revoked_at') and api_key.revoked_at:
            raise UnprocessableEntityError(
                {'source': ''}, 'API key is already revoked'
            )

    methods = ['GET', 'PATCH', 'DELETE']
    decorators = (jwt_required,)
    schema = ApiKeySchema
    data_layer = {
        'session': db.session,
        'model': ApiKey,
        'methods': {'before_update_object': before_update_object},
    }


class ApiKeyRelationship(ResourceRelationship):
    """
    API key relationships
    """

    decorators = (jwt_required,)
    schema = ApiKeySchema
    data_layer = {'session': db.session, 'model': ApiKey}
