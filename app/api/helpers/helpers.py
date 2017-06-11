import logging
from app.models import db


def save_to_db(item, msg="Saved to db", print_error=True):
    """Convenience function to wrap a proper DB save
    :param print_error:
    :param item: will be saved to database
    :param msg: Message to log
    """
    try:
        logging.info(msg)
        db.session.add(item)
        logging.info('added to session')
        db.session.commit()
        return True
    except Exception, e:
        if print_error:
            print
            e
            traceback.print_exc()
        logging.error('DB Exception! %s' % e)
        db.session.rollback()
        return False
