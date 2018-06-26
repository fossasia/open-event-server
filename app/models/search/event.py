"Models and functions for full-text search on events"
from elasticsearch_dsl import DocType, Text, Integer


class SearchableEvent(DocType):
    "Data class for putting events into Elasticsearch"
    id = Integer()
    name = Text()
    description = Text()
    location_name = Text()
    organizer_name = Text()
    organizer_description = Text()

    class Meta:
        index = 'event'

    meta = Meta()

    def from_event(self, db_event):
        "Convert an existing (sqlalchemy-)event into an Elasticsearch event"
        self.meta.id = db_event.id

        self.id = db_event.id
        self.name = db_event.name
        self.description = db_event.description
        self.location_name = db_event.location_name
        self.organizer_name = db_event.organizer_name
        self.organizer_description = db_event.organizer_description
