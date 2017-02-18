import json

import requests
from flask import Blueprint
from flask import render_template
from flask import request, redirect, url_for, jsonify
from flask.ext.restplus import abort
from flask_restplus import marshal
from requests import ConnectionError

from app.api.events import EVENT, EVENT_PAGINATED
from app.api.helpers.helpers import get_paginated_list, get_object_list
from app.helpers.data import DataGetter
from app.helpers.flask_ext.helpers import deslugify
from app.helpers.helpers import get_date_range
from app.helpers.static import EVENT_TOPICS
from app.models.event import Event

RESULTS_PER_PAGE = 10


def get_paginated(**kwargs):
    current_page = request.args.get('page')
    if current_page:
        current_page = int(current_page) - 1
        if current_page < 0:
            abort(404)
    else:
        current_page = 0

    try:
        return get_paginated_list(Event, url=request.path, args={
            'start': (current_page * RESULTS_PER_PAGE) + 1,
            'limit': RESULTS_PER_PAGE,
        }, **kwargs)
    except:
        return {
            'start': 0,
            'count': 0,
            'limit': RESULTS_PER_PAGE,
            'results': []
        }


def erase_from_dict(d, k):
    if isinstance(d, dict):
        if k in d.keys():
            d.pop(k)


def clean_dict(d):
    d = dict(d)
    return dict((k, v) for k, v in d.iteritems() if v)


def get_coordinates(location_name):

    location = {
        'lat': 0.0,
        'lng': 0.0
    }

    url = 'https://maps.googleapis.com/maps/api/geocode/json'
    params = {'address': location_name}
    response = dict()

    try:
        response = requests.get(url, params).json()
    except ConnectionError:
        response['status'] = u'Error'

    if response['status'] == u'OK':
        location = response['results'][0]['geometry']['location']

    return location


explore = Blueprint('explore', __name__, url_prefix='/explore')


@explore.route('/', methods=('GET', 'POST'))
def explore_base():
    return redirect(url_for('admin.browse_view'))


@explore.route('/autocomplete/locations.json', methods=('GET', 'POST'))
def locations_autocomplete():
    locations = DataGetter.get_locations_of_events()
    return jsonify([{'value': location, 'type': 'location'} for location in locations])


@explore.route('/autocomplete/categories.json', methods=('GET', 'POST'))
def categories_autocomplete():
    categories = EVENT_TOPICS.keys()
    return jsonify([{'value': category, 'type': 'category'} for category in categories])


@explore.route('/autocomplete/events/<location_slug>.json', methods=('GET', 'POST'))
def events_autocomplete(location_slug):
    location = deslugify(location_slug)
    results = get_object_list(Event, __event_search_location=location)
    results = marshal(results, EVENT)
    return jsonify([{'value': result['name'], 'type': 'event_name'} for result in results])


@explore.route('/<location>/events/')
def explore_view(location):
    placeholder_images = DataGetter.get_event_default_images()
    custom_placeholder = DataGetter.get_custom_placeholders()
    location = deslugify(location)
    query = request.args.get('query', '')

    filtering = {'privacy': 'public', 'state': 'Published'}
    start, end = None, None
    word = request.args.get('query', None)
    event_type = request.args.get('type', None)
    day_filter = request.args.get('period', None)
    sub_category = request.args.get('sub-category', None)
    category = request.args.get('category', None)

    if day_filter:
        start, end = get_date_range(day_filter)
    if location and location != 'world':
        filtering['__event_search_location'] = location
    if word:
        filtering['__event_contains'] = word
    if category:
        filtering['topic'] = category
    if sub_category:
        filtering['sub_topic'] = sub_category
    if event_type:
        filtering['type'] = event_type
    if start:
        filtering['__event_start_time_gt'] = start
    if end:
        filtering['__event_end_time_lt'] = end

    results = marshal(get_paginated(**filtering), EVENT_PAGINATED)
    filters = clean_dict(request.args.items())

    custom_placeholder_serializable = {}
    for custom_placeholder_item in custom_placeholder:
        custom_placeholder_serializable[custom_placeholder_item.name] = custom_placeholder_item.thumbnail

    return render_template('gentelella/guest/explore/results.html',
                           results=json.dumps(results['results']),
                           location=location if location != 'world' else '',
                           position=json.dumps(get_coordinates(location)),
                           count=results['count'],
                           query_args=json.dumps(filters),
                           placeholder_images=json.dumps(placeholder_images),
                           custom_placeholder=json.dumps(custom_placeholder_serializable),
                           categories=EVENT_TOPICS,
                           results_per_page=RESULTS_PER_PAGE,
                           query=query)
