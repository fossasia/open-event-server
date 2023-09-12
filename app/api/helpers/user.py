import datetime

import jwt
from flask import current_app
from sqlalchemy.orm.exc import NoResultFound

from app.api.helpers.db import save_to_db
from app.api.helpers.errors import ForbiddenError, UnprocessableEntityError
from app.models import db
from app.models.user import User
from app.models.user_check_in import VirtualCheckIn


def modify_email_for_user_to_be_deleted(user):
    """
    Update the email ID of user which is to be deleted.
    Adds '.deleted' substring to email of a user to be deleted.
    :param order: User to be deleted.
    :return:
    """
    not_unique_email = True
    user_email = user.email
    while not_unique_email:
        try:
            db.session.query(User).filter_by(email=user_email).one()
        except NoResultFound:
            user.email = user_email
            save_to_db(user)
            not_unique_email = False
        else:
            user_email = user_email + '.deleted'
    return user


def modify_email_for_user_to_be_restored(user):
    """
    Update the email ID of user which is to be restored.
    Removes '.deleted' substring from a user to be restored.
    :param order: User to be restored.
    :return:
    """
    user_email = user.email
    remove_str = '.deleted'
    if user_email.endswith(remove_str):
        user_email = user_email[: -len(remove_str)]
        try:
            db.session.query(User).filter_by(email=user_email).one()
        except NoResultFound:
            user.email = user_email
            save_to_db(user)
        else:
            raise ForbiddenError(
                {'pointer': '/data/attributes/email'},
                "This email is already registered! Manually edit and then try restoring",
            )
    return user


def get_user_id_from_token(token: str):
    """
    Get user Id from JWT token
    @param token: JWT token
    @return: user id
    """
    data = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
    if not data.get('identity', False):
        return {"message": "Can't get user id!", "data": None}, 404

    return data["identity"]


def virtual_event_check_in(data, attendee_ids, event_id):
    """
    do check in for attendee in virtual event
    @param data: data
    @param attendee_ids: attendee_ids
    @param event_id: event_id
    """
    current_time = datetime.datetime.now()
    if data['is_check_in']:
        virtual_check_in = VirtualCheckIn(
            ticket_holder_id=attendee_ids,
            event_id=event_id,
            check_in_type=data['check_in_type'],
            check_in_at=current_time,
            microlocation_id=data.get('microlocation_id'),
        )
    else:
        virtual_check_in = (
            VirtualCheckIn.query.filter(
                VirtualCheckIn.ticket_holder_id == attendee_ids,
                VirtualCheckIn.event_id == event_id,
                VirtualCheckIn.microlocation_id == data.get('microlocation_id'),
            )
            .order_by(VirtualCheckIn.id.desc())
            .first()
        )
        if virtual_check_in is None:
            raise UnprocessableEntityError({'errors': 'Attendee not check in yet'})
        if virtual_check_in.check_out_at is not None:
            raise UnprocessableEntityError({'errors': 'Attendee Already checked out'})
        virtual_check_in.check_out_at = current_time
    save_to_db(virtual_check_in)
