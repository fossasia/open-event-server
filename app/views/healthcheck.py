from app.models import db
from celery.task.control import inspect
from errno import errorcode
import json
from flask import current_app


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


def safe_dump(skip_words, dictionary):
    """
    Modified version of safe_dump function from healthcheck library to accept custom substrings to skip in output
    :param skip_words:
    :param dictionary:
    :return:
    """
    result = {}
    for key in dictionary.keys():
        if any(x in key.lower() for x in skip_words):
            # Try to avoid listing passwords and access tokens or keys in the output
            result[key] = "********"
        else:
            try:
                json.dumps(dictionary[key])
                result[key] = dictionary[key]
            except TypeError:
                pass
    return result


def get_safe_config():
    """
    Get safe config
    :return:
    """
    skip_words = ['key', 'pass', 'dsn', 'database_uri', 'token']
    return safe_dump(skip_words, current_app.config)
