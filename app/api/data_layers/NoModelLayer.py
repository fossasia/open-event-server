from flask_rest_jsonapi.data_layers.base import BaseDataLayer

from app.api.helpers.utilities import EmptyObject


class NoModelLayer(BaseDataLayer):
    def get_object(self, view_kwargs):
        """Retrieve an object
        :params dict view_kwargs: kwargs from the resource view
        :return DeclarativeMeta: an object
        """
        obj = EmptyObject()
        obj.id = 1
        return obj
