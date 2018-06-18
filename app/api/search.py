"""Elasticsearch resource for querying events

Uses the events index to filter for all events. Can use more specific queries
for `location_name`, `name` and description.
"""

from flask import request
from flask_rest_jsonapi.resource import Resource
from elasticsearch_dsl import Search

from app.models.search.event import SearchableEvent
from app.views.elastic_search import es


def to_dict(response):
    "Converts elasticsearch responses to dicts for serialization"
    r = response.to_dict()
    r['meta'] = response.meta.to_dict()

    return r


class SearchEvent(Resource):
    """Resource for event searches

    Queries elasticsearch for events using fuzzy matches for names, locations
    and descriptions
    """

    def get(self, query):
        args = request.args
        search = Search(using=es, index=SearchableEvent.meta.index)

        if args.get('name'):
            search = search.query('fuzzy', name=args['name'])
            search = search.highlight('name')

        if args.get('description'):
            search = search.query('fuzzy', description=args['description'])
            search = search.highlight('description')

        if args.get('location_name'):
            search = search.query('fuzzy', location_name=args['location_name'])
            search = search.highlight('location_name')

        return [to_dict(r) for r in search.execute()]
