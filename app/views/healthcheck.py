from errno import errorcode

from redis.exceptions import ConnectionError
from sentry_sdk import capture_exception, capture_message

from app.models import db


def health_check_celery():
    """
    Check health status of celery and redis broker
    :return:
    """
    from app.api.helpers.tasks import celery

    try:
        d = celery.control.inspect().stats()
        if not d:
            capture_message('No running Celery workers were found.')
            return False, 'No running Celery workers were found.'
    except ConnectionError as e:
        capture_exception(e)
        return False, 'cannot connect to redis server'
    except OSError as e:
        msg = "Error connecting to the backend: " + str(e)
        if len(e.args) > 0 and errorcode.get(e.args[0]) == 'ECONNREFUSED':
            msg += ' Check that the Redis server is running.'
        capture_exception(e)
        return False, msg
    except ImportError as e:
        capture_exception(e)
        return False, str(e)
    except Exception:
        capture_exception()
        return False, 'celery not ok'
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
        capture_exception()
        return False, 'Error connecting to database'


def check_migrations():
    """
    Checks whether database is up to date with migrations by performing a select query on each model
    :return:
    """
    # Get all the models in the db, all models should have a explicit __tablename__
    classes, models, table_names = [], [], []
    # noinspection PyProtectedMember
    for class_ in list(db.Model._decl_class_registry.values()):
        try:
            table_names.append(class_.__tablename__)
            classes.append(class_)
        except:
            pass
    for table in list(db.metadata.tables.items()):
        if table[0] in table_names:
            models.append(classes[table_names.index(table[0])])

    for model in models:
        try:
            db.session.query(model).first()
        except:
            capture_exception()
            return f'failure,{model} model out of date with migrations'
    return 'success,database up to date with migrations'


def health_check_migrations():
    result = check_migrations().split(',')
    if result[0] == 'success':
        return True, result[1]
    # the exception will be caught in check_migrations function, so no need for sentry catching exception here
    return False, result[1]
