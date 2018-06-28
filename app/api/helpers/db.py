import logging
import traceback

from flask_rest_jsonapi.exceptions import ObjectNotFound
from sqlalchemy import func
from sqlalchemy.orm.exc import NoResultFound

from app.models import db


# ONLY INCLUDE THOSE DB HELPERS WHICH ARE NOT SPECIFIC TO ANY MODEL


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
    except Exception as e:
        if print_error:
            print(e)
            traceback.print_exc()
        logging.error('DB Exception! %s' % e)
        db.session.rollback()
        return False


def safe_query_without_soft_deleted_entries(self, model, column_name, value, parameter_name):
    """
    Wrapper query to properly raise exception after filtering the soft deleted entries
    :param self:
    :param model: db Model to be queried
    :param column_name: name of the column to be queried for the given value
    :param value: value to be queried against the given column name, e.g view_kwargs['event_id']
    :param parameter_name: Name of parameter to be printed in json-api error message eg 'event_id'
    :return:
    """
    try:
        if hasattr(model, 'deleted_at'):
            record = self.session.query(model).filter(getattr(model, column_name) == value)\
                .filter_by(deleted_at=None).one()
        else:
            record = self.session.query(model).filter(getattr(model, column_name) == value).one()
    except NoResultFound:
        raise ObjectNotFound({'parameter': '{}'.format(parameter_name)},
                             "{}: {} not found".format(model.__name__, value))
    else:
        return record


def safe_query(self, model, column_name, value, parameter_name):
    """
    Wrapper query to properly raise exception
    :param self:
    :param model: db Model to be queried
    :param column_name: name of the column to be queried for the given value
    :param value: value to be queried against the given column name, e.g view_kwargs['event_id']
    :param parameter_name: Name of parameter to be printed in json-api error message eg 'event_id'
    :return:
    """
    try:
        record = self.session.query(model).filter(getattr(model, column_name) == value).one()
    except NoResultFound:
        raise ObjectNotFound({'parameter': '{}'.format(parameter_name)},
                             "{}: {} not found".format(model.__name__, value))
    else:
        return record


def get_or_create(model, **kwargs):
    """
    This function queries a record in the model, if not found it will create one.
    :param model: db Model to be queried
    :param **kwargs: Arguments to the filter_by method of sqlalchemy.orm.query.Query.filter_by to be filtered by
    """
    was_created = False
    instance = db.session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance, was_created
    else:
        instance = model(**kwargs)
        db.session.add(instance)
        db.session.commit()
        was_created = True
        return instance, was_created


def get_count(query):
    """
    Counts how many records are there in a database table/model
    :param query: <sqlalchemy.orm.query.Query> a SQLAlchemy query object
    :return: Number
    """
    count_q = query.statement.with_only_columns([func.count()]).order_by(None)
    count = query.session.execute(count_q).scalar()
    return count
