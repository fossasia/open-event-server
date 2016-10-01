"""Copyright 2015 Rafal Kowalski"""


class QueryFilter(object):
    """Query filter class"""
    def __init__(self, args, query):
        self.args = args
        self.query = query

    def get_filtered_data(self):
        """Returns Filtered data"""
        filters = {}
        column = None

        for key, value in list(dict(self.args).items()):
            filters[key] = ''.join(value)

        if "order_by" in list(filters.keys()):
            column = filters["order_by"]
            del filters["order_by"]

        return self.query.filter_by(**filters).order_by(column)

    @staticmethod
    def get_query_list(query):
        """Returns list query"""
        rows = []
        for u in query:
            rows.append(u.__dict__)
        return rows
