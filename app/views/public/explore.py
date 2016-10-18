from flask.ext.restplus import abort
from flask_admin import BaseView, expose

from flask_restplus import marshal
from app.api.events import EVENT
from app.api.helpers.helpers import get_paginated_list, get_object_list
from app.helpers.flask_helpers import deslugify
from app.helpers.helpers import get_date_range
from app.helpers.data import DataGetter
from app.models.event import Event
from flask import request, redirect, url_for, jsonify


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

class ExploreView(BaseView):

    @expose('/', methods=('GET', 'POST'))
    def explore_base(self):
        return redirect(url_for('admin.browse_view'))

    @expose('/autocomplete/locations.json', methods=('GET', 'POST'))
    def locations_autocomplete(self):
        locations = DataGetter.get_locations_of_events()
        return jsonify([{'value': location, 'type': 'location'} for location in locations])

    @expose('/autocomplete/categories.json', methods=('GET', 'POST'))
    def categories_autocomplete(self):
        categories = CATEGORIES.keys()
        return jsonify([{'value': category, 'type': 'category'} for category in categories])

    @expose('/autocomplete/events/<location_slug>.json', methods=('GET', 'POST'))
    def events_autocomplete(self, location_slug):
        location = deslugify(location_slug)
        results = get_object_list(Event, __event_search_location=location)
        results = marshal(results, EVENT)
        return jsonify([{'value': result['name'], 'type': 'event_name'} for result in results])

    @expose('/<location>/events/', methods=('GET', 'POST'))
    def explore_view(self, location):
        placeholder_images = DataGetter.get_event_default_images()
        custom_placeholder = DataGetter.get_custom_placeholders()
        location = deslugify(location)
        current_page = request.args.get('page')
        query = request.args.get('query', '')
        if not current_page:
            current_page = 1
        else:
            current_page = int(current_page)

        filtering = {'privacy': 'public', 'state': 'Published'}
        start, end = None, None
        word = request.args.get('query', None)
        event_type = request.args.get('type', None)
        day_filter = request.args.get('period', None)
        sub_category = request.args.get('sub-category', None)
        category = request.args.get('category', None)

        if day_filter:
            start, end = get_date_range(day_filter)
        if location:
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
        filters = request.args.items()
        erase_from_dict(filters, 'page')
        results = get_paginated(**filtering)

        return self.render('/gentelella/guest/search/results.html',
                           results=results,
                           location=location,
                           filters=filters,
                           current_page=current_page,
                           placeholder_images=placeholder_images,
                           custom_placeholder=custom_placeholder,
                           categories=CATEGORIES, query=query)


CATEGORIES = {'Auto, Boat & Air': ['Air', 'Auto', 'Boat', 'Motorcycle/ATV', 'Other'],
              'Business & Professional':
                  ['Career', 'Design', 'Educators', 'Environment &amp; Sustainability', 'Finance', 'Media',
                   'Non Profit &amp; NGOs', 'Other', 'Real Estate', 'Sales &amp; Marketing',
                   'Startups &amp; Small Business'],
              'Charity & Causes': ['Animal Welfare', 'Disaster Relief', 'Education', 'Environment', 'Healthcare',
                                   'Human Rights', 'International Aid', 'Other', 'Poverty'],
              'Community & Culture': ['City/Town', 'County', 'Heritage', 'LGBT', 'Language', 'Medieval', 'Nationality',
                                      'Other', 'Renaissance', 'State'],
              'Family & Education': ['Alumni', 'Baby', 'Children &amp; Youth', 'Education', 'Other', 'Parenting',
                                     'Parents Association', 'Reunion'],
              'Fashion & Beauty': ['Accessories', 'Beauty', 'Bridal', 'Fashion', 'Other'],
              'Film, Media & Entertainment': ['Adult', 'Anime', 'Comedy', 'Comics', 'Film', 'Gaming', 'Other', 'TV'],
              'Food & Drink': ["Beer", "Food", "Other", "Spirits", "Wine"],
              'Government & Politics': ["County/Municipal Government ", "Democratic Party", "Federal Government",
                                        "Non-partisan", "Other", "Other Party", "Republican Party", "State Government"],
              'Health & Wellness': ["Medical", "Mental health", "Other", "Personal health", "Spa", "Yoga"],
              'Hobbies & Special Interest': ["Adult", "Anime/Comics", "Books", "DIY", "Drawing & Painting",
                                             "Gaming", "Knitting", "Other", "Photography"],
              'Home & Lifestyle': ["Dating", "Home & Garden", "Other", "Pets & Animals"],
              'Music': ["Alternative", "Blues & Jazz", "Classical", "Country", "Cultural", "EDM / Electronic",
                        "Folk", "Hip Hop / Rap", "Indie", "Latin", "Metal", "Opera", "Other", "Pop", "R&B", "Reggae",
                        "Religious/Spiritual", "Rock", "Top 40"],
              'Other': [],
              'Performing & Visual Arts': ["Ballet", "Comedy", "Craft", "Dance", "Fine Art", "Literary Arts", "Musical",
                                           "Opera", "Orchestra", "Other", "Theatre"],
              'Religion & Spirituality': ["Buddhism", "Christianity", "Eastern Religion", "Islam", "Judaism",
                                          "Mormonism", "Mysticism and Occult", "New Age", "Other", "Sikhism"],
              'Science & Technology': ["Biotech", "High Tech", "Medicine", "Mobile", "Other", "Robotics",
                                       "Science", "Social Media"],
              'Seasonal & Holiday': ["Channukah", "Christmas", "Easter", "Fall events", "Halloween/Haunt",
                                     "Independence Day", "New Years Eve", "Other", "St Patricks Day", "Thanksgiving"],
              'Sports & Fitness': ["Baseball", "Basketball", "Cycling", "Exercise", "Fighting & Martial Arts",
                                   "Football", "Golf", "Hockey", "Motorsports", "Mountain Biking", "Obstacles",
                                   "Other", "Rugby", "Running", "Snow Sports", "Soccer", "Swimming & Water Sports",
                                   "Tennis", "Volleyball", "Walking", "Yoga"],
              'Travel & Outdoor': ["Canoeing", "Climbing", "Hiking", "Kayaking", "Other", "Rafting", "Travel"]
              }
