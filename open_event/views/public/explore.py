from flask.ext.restplus import abort
from flask_admin import BaseView, expose

from open_event.api.helpers.helpers import get_paginated_list
from open_event.helpers.flask_helpers import deslugify
from open_event.helpers.helpers import get_date_range
from open_event.models.event import Event
from flask import request, redirect, url_for

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
        return get_paginated_list(Event, request.path, {
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
            print(d)

class ExploreView(BaseView):

    @expose('/', methods=('GET', 'POST'))
    def explore_base(self):
        return redirect(url_for('admin.browse_view'))

    @expose('/<location>/events', methods=('GET', 'POST'))
    def explore_view(self, location):
        location = deslugify(location)
        current_page = request.args.get('page')
        if not current_page:
            current_page = 1
        else:
            current_page = int(current_page)

        filtering = {'privacy': 'public', 'state': 'Published'}
        start, end = None, None
        word = request.form.get('word', '')
        event_type = request.args.get('event_type', '')
        day_filter = request.args.get('day', '')
        if day_filter:
            start, end = get_date_range(day_filter)
        if location:
            filtering['__event_location'] = location
        if word:
            filtering['__event_contains'] = word
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
                           categories=CATEGORIES)


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
