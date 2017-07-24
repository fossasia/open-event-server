from app.models import db
from celery.task.control import inspect
from errno import errorcode


def health_check_celery():
    """
    Check health status of celery and redis broker
    :return:
    """
    try:
        d = inspect().stats()
        if not d:
            return False, 'No running Celery workers were found.'
    except IOError as e:
        msg = "Error connecting to the backend: " + str(e)
        if len(e.args) > 0 and errorcode.get(e.args[0]) == 'ECONNREFUSED':
            msg += ' Check that the Redis server is running.'
        return False, msg
    except ImportError as e:
        return False, str(e)
    return True, 'celery ok'


def health_check_db():
    """
    Check health status of db
    :return:
    """
    try:
        db.session.execute('SELECT 1')
        return True, 'database ok'
    except:
        return False, 'Error connecting to database'
