from flask_rest_jsonapi.data_layers.base import BaseDataLayer

from app.api.helpers.db import safe_query, save_to_db
from app.api.helpers.exceptions import UnprocessableEntity
from app.api.helpers.utilities import get_serializer
from app.models.user import User


class VerifyUserLayer(BaseDataLayer):
    def create_object(self, data, view_kwargs):
        user = safe_query(self, User, 'id', view_kwargs['user_id'], 'user_id')
        s = get_serializer()
        try:
            data = s.loads(data['token'])
        except Exception:
            raise UnprocessableEntity({'source': 'token'}, "Invalid Token")

        if user.email == data[0]:
            user.is_verified = True
            save_to_db(user)
            return user
        else:
            raise UnprocessableEntity({'source': 'token'}, "Invalid Token")
