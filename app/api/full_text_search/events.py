"""Elasticsearch resource for querying events

Uses the events index to filter for all events. Can use more specific queries
for `location_name`, `name` and description.
"""

from elasticsearch_dsl import Search
from flask import request
from flask_rest_jsonapi.resource import Resource

from app.models.search.event import SearchableEvent
from app.views.elastic_search import client


def to_dict(response):
    """
    Converts elasticsearch responses to dicts for serialization
    """
    r = response.to_dict()
    r['meta'] = response.meta.to_dict()

    return r


class EventSearchResultList(Resource):
    """Resource for event searches

    Queries elasticsearch for events using fuzzy matches for names, locations
    and descriptions
    """

    def search(self, args, es_client=client):
        search = Search(using=es_client, index=SearchableEvent.meta.index)

        if args.get('name'):
            search = search.query('fuzzy', name=args['name'])
            search = search.highlight('name')

        if args.get('description'):
            search = search.query('match', description=args['description'])
            search = search.highlight('description')

        if args.get('location-name'):
            search = search.query('fuzzy', location_name=args['location_name'])
            search = search.highlight('location_name')

        if args.get('owner-name'):
            search = search.query('fuzzy', owner_name=args['owner_name'])
            search = search.highlight('owner_name')

        if args.get('owner-description'):
            search = search.query('fuzzy', owner_description=args['owner_description'])
            search = search.highlight('owner_description')

        return [to_dict(r) for r in search.execute()]

    def get(self):
        args = request.args

        return self.search(args)
