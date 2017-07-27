from app.models import db
from celery.task.control import inspect
from errno import errorcode
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


def check_migrations():
    """
    Checks whether database is up to date with migrations by performing a select query on each model
    :return:
    """
    print("Checking if migrations are up to date.....")
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
        except Exception as e:
            print(e)
            print("failure: {} model out of date with migrations.....".format(model))
            return 'failure,{} model out of date with migrations'.format(model)
    print("success: database up to date with migrations.....")
    return 'success,database up to date with migrations'


def health_check_migrations():
    """
    Parses config var 'MIGRATION_STATUS' obtained from check_migrations function
    :return:
    """
    if 'MIGRATION_STATUS' in current_app.config:
        result = current_app.config['MIGRATION_STATUS'].split(',')
        if result[0] == 'success':
            return True, result[1]
        else:
            return False, result[0]
    else:
        return False, 'The health_check_migration test is still running'
