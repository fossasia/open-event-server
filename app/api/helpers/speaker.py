from datetime import datetime

from app.api.helpers.errors import ForbiddenError
from app.api.helpers.permission_manager import has_access
from app.models.speakers_call import SpeakersCall


def can_edit_after_cfs_ends(event_id):
    """
    Method to check that user has permission to edit the speaker or session
    after the CFS ends
    """
    speakers_call = SpeakersCall.query.filter_by(
        event_id=event_id, deleted_at=None
    ).one_or_none()
    if speakers_call:
        speakers_call_tz = speakers_call.ends_at.tzinfo
        return not (
            speakers_call.ends_at <= datetime.now().replace(tzinfo=speakers_call_tz)
            and not (
                has_access('is_admin')
                or has_access('is_organizer', event_id=event_id)
                or has_access('is_coorganizer', event_id=event_id)
            )
        )
    else:
        raise ForbiddenError(
            {'source': '/data/event-id'},
            'Speaker Calls for event {id} not found'.format(id=event_id),
        )
