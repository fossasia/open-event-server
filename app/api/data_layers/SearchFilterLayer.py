from flask_rest_jsonapi.data_layers.alchemy import SqlalchemyDataLayer


class SearchFilterLayer(SqlalchemyDataLayer):
    def filter_query(self, query, filter_info, model):
        """Filter query according to jsonapi 1.0
        :param Query query: sqlalchemy query to sort
        :param filter_info: filter information
        :type filter_info: dict or None
        :param DeclarativeMeta model: an sqlalchemy model
        :return Query: the sorted query
        """
        without_fulltext = [f for f in filter_info if f['op'] != 'search']

        if not without_fulltext:
            return query

        return super().filter_query(query, without_fulltext, model)
