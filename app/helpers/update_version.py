"""Copyright 2015 Rafal Kowalski"""
from ..models import db
from ..models.version import Version


class VersionUpdater(object):
    """Version Update class"""
    def __init__(self, is_created, event_id, column_to_increment):
        self.is_created = is_created
        self.column_to_increment = column_to_increment
        self.event_id = event_id

    def update(self):
        """Update version in db"""
        previous_version = Version.query.filter_by(event_id=self.event_id) \
                                        .order_by(Version.id.desc()).first()
        if not previous_version:
            version = Version(event_id=self.event_id)
            db.session.add(version)
            db.session.commit()
        else:
            self._create_new_version(previous_version)

    def _create_new_version(self, previous_version):
        prv_value = getattr(previous_version, self.column_to_increment, 0)
        if not prv_value:
            prv_value = 0
        setattr(previous_version, self.column_to_increment, prv_value + 1)
        db.session.add(previous_version)
        db.session.commit()

    def set(self, data):
        """Set version info of an event to data"""
        previous_version = Version.query.filter_by(event_id=self.event_id) \
                                        .order_by(Version.id.desc()).first()
        if not previous_version:
            previous_version = Version(event_id=self.event_id, **data)
        else:
            for key in data:
                setattr(previous_version, key, data[key])
        db.session.add(previous_version)
        db.session.commit()


def get_all_columns():
    return [
        'event_ver', 'sessions_ver', 'speakers_ver', 'sponsors_ver',
        'tracks_ver', 'microlocations_ver'
    ]
