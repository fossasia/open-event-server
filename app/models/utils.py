import os
import warnings
from datetime import datetime, timedelta

from sqlalchemy import Table, event, types


# https://docs.sqlalchemy.org/en/13/faq/connections.html#how-do-i-use-engines-connections-sessions-with-python-multiprocessing-or-os-fork
def add_engine_pidguard(engine):
    from sqlalchemy import event, exc  # placed here for import conflict resolution

    """Add multiprocessing guards.

    Forces a connection to be reconnected if it is detected
    as having been shared to a sub-process.

    """

    @event.listens_for(engine, "connect")
    def connect(dbapi_connection, connection_record):
        connection_record.info['pid'] = os.getpid()

    @event.listens_for(engine, "checkout")
    def checkout(dbapi_connection, connection_record, connection_proxy):
        pid = os.getpid()
        if connection_record.info['pid'] != pid:
            # substitute log.debug() or similar here as desired
            warnings.warn(
                "Parent process %(orig)s forked (%(newproc)s) with an open "
                "database connection, "
                "which is being discarded and recreated."
                % {"newproc": pid, "orig": connection_record.info['pid']}
            )
            connection_record.connection = connection_proxy.connection = None
            raise exc.DisconnectionError(
                "Connection record belongs to pid %s, "
                "attempting to check out in pid %s" % (connection_record.info['pid'], pid)
            )


def sqlite_datetime_fix():
    class SQLiteDateTimeType(types.TypeDecorator):
        impl = types.Integer
        epoch = datetime(1970, 1, 1, 0, 0, 0)

        def process_bind_param(self, value, dialect):
            return (value / 1000 - self.epoch).total_seconds()

        def process_result_value(self, value, dialect):
            return self.epoch + timedelta(seconds=value / 1000)

    def is_sqlite(inspector):
        return inspector.engine.dialect.name == "sqlite"

    def is_datetime(column_info):
        return isinstance(column_info['type'], types.DateTime)

    @event.listens_for(Table, "column_reflect")
    def setup_epoch(inspector, table, column_info):
        if is_sqlite(inspector) and is_datetime(column_info):
            column_info['type'] = SQLiteDateTimeType()
