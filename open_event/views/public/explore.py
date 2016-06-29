from flask.ext.restplus import abort
from flask_admin import BaseView, expose

from open_event.api.helpers.helpers import get_paginated_list
from open_event.helpers.flask_helpers import deslugify
from open_event.helpers.helpers import get_date_range
from open_event.models.event import Event
from flask import request, redirect, url_for

RESULTS_PER_PAGE = 2

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
                           current_page=current_page)

