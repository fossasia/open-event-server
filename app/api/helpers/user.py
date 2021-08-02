from sqlalchemy.orm.exc import NoResultFound

from app.api.helpers.db import save_to_db
from app.api.helpers.errors import ForbiddenError
from app.models import db
from app.models.user import User


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
