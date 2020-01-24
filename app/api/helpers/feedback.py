import logging

from app.models import db

logger = logging.getLogger(__name__)


def delete_feedback(feedback):
    """
    Delete the feedback if rating is zero
    :param feedback: Feedback to be deleted
    :return:
    """
    db.session.delete(feedback)
    try:
        db.session.commit()
    except Exception:
        logger.exception('Feedback delete exception!')
        db.session.rollback()
