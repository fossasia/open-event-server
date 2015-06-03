"""Written by - Rafal Kowalski"""
from .event import Event
from .version import Version
from sqlalchemy.event import listens_for


@listens_for(Event, "after_insert")
def after_insert(mapper, connection, target):
    link_table = Version.__table__
    version_id = Version.query.order_by(Version.id.desc()).first().id
    connection.execute(
        link_table.update().
        where(link_table.c.id == version_id).
        values(event_id=target.id))
