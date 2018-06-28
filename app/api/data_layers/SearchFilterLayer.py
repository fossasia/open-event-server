from flask_rest_jsonapi.data_layers.alchemy import SqlalchemyDataLayer, create_filters

from app.api.helpers.utilities import EmptyObject


class SearchFilterLayer(SqlalchemyDataLayer):
    def filter_query(self, query, filter_info, model):
        """Filter query according to jsonapi 1.0
        :param Query query: sqlalchemy query to sort
        :param filter_info: filter information
        :type filter_info: dict or None
        :param DeclarativeMeta model: an sqlalchemy model
        :return Query: the sorted query
        """
        without_fulltext = [f for f in filter_info if f.get('op') and f['op'] != 'search']

        if without_fulltext:
            print(without_fulltext)
            filters = create_filters(model, without_fulltext, self.resource)
            query = query.filter(*filters)
