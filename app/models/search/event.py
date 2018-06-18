from elasticsearch_dsl import DocType, Text, Integer


class SearchableEvent(DocType):
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
        self.meta.id = db_event.id

        self.id = db_event.id
        self.description = db_event.description
        self.location_name = db_event.location_name
        self.organization_name = db_event.organizer_name
        self.organization_description = db_event.organizer_description

    def serialize(self):
        return {
            'name': self.name,
            'description': self.description,
            'location_name': self.location_name,
            'organizer_name': self.organization_name,
        }
