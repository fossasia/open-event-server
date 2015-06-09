"""Written by - Rafal Kowalski"""


class QueryFilter(object):
    def __init__(self, args, query):
        self.args = args
        self.query = query

    def get_filtered_data(self):
        filters = {}
        column = None

        for key, value in dict(self.args).items():
            filters[key] = ''.join(value)

        if "order_by" in filters.keys():
            column = filters["order_by"]
            del filters["order_by"]

        return self.query.filter_by(**filters).order_by(column)
    @staticmethod
    def get_query_list(query):
        rows = []
        for u in query:
             rows.append(u.__dict__)
        return rows