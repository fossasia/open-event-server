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


def health_check_migrations():
    """
    Checks whether database is up to date with migrations by performing a select query on each model
    :return:
    """
    # Get all the models in the db, all models should have a explicit __tablename__
    classes, models, table_names = [], [], []
    # noinspection PyProtectedMember
    for class_ in db.Model._decl_class_registry.values():
        try:
            table_names.append(class_.__tablename__)
            classes.append(class_)
        except:
            pass
    for table in db.metadata.tables.items():
        if table[0] in table_names:
            models.append(classes[table_names.index(table[0])])

    for model in models:
        try:
            db.session.query(model).first()
        except:
            return False, '{} model out of date with migrations'.format(model)
    return True, 'database up to date with migrations'
