import logging

from app.models import db
from app.models.role_invite import RoleInvite

logger = logging.getLogger(__name__)


def delete_previous_uer(uer):
    """
    delete previous owner before adding a new one
    :param uer: User Event Role to be deleted.
    :return:
    """
    role_invite = (
        db.session.query(RoleInvite)
        .filter_by(
            email=uer.user.email,
            event_id=uer.event_id,
            role_name='owner',
            status='accepted',
        )
        .first()
    )

    if role_invite:
        db.session.delete(role_invite)
    db.session.delete(uer)
    try:
        db.session.commit()
    except Exception:
        logger.exception('UER or Role Invite delete exception!')
        db.session.rollback()
