from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from app.models.event_type import EventType


class EventTypeSchema(SQLAlchemyAutoSchema):
    """
    Using SQLAlchemyAutoSchema of marshmallow_sqlalchemy
    """
    class Meta:
        model = EventType
        include_relationships = True
        include_fk = True
        load_instance = True
