from sqlalchemy import or_, func

from open_event.helpers.helpers import get_date_range
from open_event.models.event import Event
from custom_fields import DateTime


def extract_special_queries(queries):
    """
    Separate special queries from normal queries
    """
    specials = {}
    dc = queries.copy()
    for i in queries:
        if i.startswith('__') and i in FILTERS_LIST:
            specials[i] = queries[i]
            del dc[i]
    return (dc, specials)


def apply_special_queries(query, specials):
    """
    Apply all special queries on the current
    existing :query (set)
    """
    for i in specials:
        query = FILTERS_LIST[i](specials[i], query)
    return query


#######
# DEFINE CUSTOM FILTERS BELOW
#######


def event_contains(value, query):
    value = value.lower()
    q = query.filter(or_(
        func.lower(Event.name).contains(value),
        func.lower(Event.description).contains(value)
    ))
    return q


def event_location(value, query):
    """
    Return all queries which contain either A or B or C
    when location is A,B,C
    TODO: Proper ordering of results a/c proximity
    """
    locations = list(value.split(','))
    queries = []
    for i in locations:
        queries.append(func.lower(Event.location_name).contains(i.lower()))
    return query.filter(or_(*queries))


def event_start_time_gt(value, query):
    return query.filter(Event.start_time >= DateTime().from_str(value))


def event_start_time_lt(value, query):
    return query.filter(Event.start_time <= DateTime().from_str(value))


def event_end_time_gt(value, query):
    return query.filter(Event.end_time >= DateTime().from_str(value))


def event_end_time_lt(value, query):
    return query.filter(Event.end_time <= DateTime().from_str(value))

def event_time_period(value, query):
    start, end = get_date_range(value)
    if start:
        query = event_start_time_gt(start, query)
    if end:
        query = event_end_time_lt(end, query)
    return query

#######
# ADD CUSTOM FILTERS TO LIST
#######


FILTERS_LIST = {
    '__event_contains': event_contains,
    '__event_location': event_location,
    '__event_start_time_gt': event_start_time_gt,
    '__event_start_time_lt': event_start_time_lt,
    '__event_end_time_gt': event_end_time_gt,
    '__event_end_time_lt': event_end_time_lt,
    '__event_time_period': event_time_period,
}
