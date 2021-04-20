from flask import Blueprint
from flask_combo_jsonapi import Api
from flask_combo_jsonapi.plugin import BasePlugin
from flask_combo_jsonapi.querystring import QueryStringManager
from sqlalchemy.orm import Query

from app.api.helpers.permission_manager import permission_manager


class dasherize_plugin(BasePlugin):
    def _update_query(
        self,
        *args,
        query: Query = None,
        qs: QueryStringManager = None,
        view_kwargs=None,
        self_json_api=None,
        **kwargs,
    ) -> Query:
        import json
        import logging

        logging.error('called 1 time')
        all_fields = self_json_api.model.__mapper__.column_attrs.keys()
        short_format = (
            self_json_api.short_format
            if hasattr(self_json_api, 'short_format')
            else all_fields
        )
        full_format = (
            self_json_api.full_formaat
            if hasattr(self_json_api, 'full_format')
            else all_fields
        )
        fields = short_format if qs.qs.get('format') == 'short' else full_format
        filters = qs.qs['filter']
        sort = qs.qs['sort']
        logging = logging.getLogger(__name__)
        json_filter_list = json.loads(filters)
        logging.error('%s ', type(json_filter_list))
        for dict in json_filter_list:
            dict = change_keys(obj=dict, convert=convert)
            logging.error('%s %s', type(dict), dict)

        sort_list = sort.split(',')
        for items in sort_list:
            items = convert(items)
        sort_string = ','.join(sort_list)

        query = self_json_api.session.query(
            *[getattr(self_json_api.model, name_field) for name_field in fields]
        )
        return query

    def data_layer_get_collection_update_query(
        self,
        *args,
        query: Query = None,
        qs: QueryStringManager = None,
        view_kwargs=None,
        self_json_api=None,
        **kwargs,
    ) -> Query:
        return self._update_query(
            *args,
            query=query,
            qs=qs,
            view_kwargs=view_kwargs,
            self_json_api=self_json_api,
            **kwargs,
        )


api_v1 = Blueprint('v1', __name__, url_prefix='/v1')
api = Api(blueprint=api_v1, plugins=[dasherize_plugin()])
api.permission_manager(permission_manager)


def change_keys(obj, convert):
    """
    Recursively goes through the dictionary obj and replaces keys with the convert function.
    """
    if isinstance(obj, (str, int, float)):
        return obj
    if isinstance(obj, dict):
        new = obj.__class__()
        for k, v in obj.items():
            new[convert(k)] = change_keys(convert(v), convert)
    elif isinstance(obj, (list, set, tuple)):
        new = obj.__class__(change_keys(v, convert) for v in obj)
    else:
        return obj
    return new


def convert(k):
    if isinstance(k, str):
        return k.replace('-', '_')
    return k
