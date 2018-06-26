"Models and functions for full-text search on events"
from elasticsearch_dsl import DocType, Integer, Search, Text

from app.api.helpers import elastic
from app.views.elastic_search import client


class SearchableEvent(DocType):
    "Data class for putting events into Elasticsearch"

    class Meta:
        index = 'event'

    def __init__(self):
        id = Integer()
        name = Text()
        description = Text()
        location_name = Text()
        organizer_name = Text()
        organizer_description = Text()
        meta = self.Meta()

    def from_event(self, db_event):
        "Convert an existing (sqlalchemy-)event into an Elasticsearch event"
        self.meta.id = db_event.id

        self.id = db_event.id
        self.name = db_event.name
        self.description = db_event.description
        self.location_name = db_event.location_name
        self.organizer_name = db_event.organizer_name
        self.organizer_description = db_event.organizer_description


def find_ids(search_strings, client=client):
    search = Search().using(client)

    for search_string in search_strings:
        search = search.query('multi_match', query=search_string)

    return [event.id for event in search.execute()]
