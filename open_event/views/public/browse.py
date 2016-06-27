from flask.ext.restplus import abort
from flask_admin import BaseView, expose

from open_event.api.helpers.helpers import get_paginated_list
from open_event.models.event import Event
from flask import request
from flask_restplus import marshal
from open_event.api.events import DAO as EventDAO, EVENT

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

class BrowseView(BaseView):
    @expose('/', methods=('GET', 'POST'))
    def browse(self, location):
        current_page = request.args.get('page')
        if not current_page:
            current_page = 1
        else:
            current_page = int(current_page)
        results = get_paginated(privacy='public', state='Published')
        return self.render('/gentelella/guest/search/results.html', results=results, location=location,
                           current_page=current_page)

    @expose('/s', methods=('GET', 'POST'))
    def browses(self, location):
        current_page = request.args.get('page')
        if not current_page:
            current_page = 1
        else:
            current_page = int(current_page)
        results = get_paginated(__event_location=location, privacy='public', state='Published')
        filters = request.args.items()
        erase_from_dict(filters, 'page')
        if request.method == "POST":
            word = request.form['word']
            event_type = request.args.get('event_type', '')
            day_filter = request.args.get('day', '')
            if location and word and event_type:
                results = marshal(
                    EventDAO.list(__event_location=location,
                                  __event_contains=word,
                                  privacy='public',
                                  state='Published',
                                  type=event_type),
                    EVENT)
            if location and word:
                results = get_paginated(__event_location=location, __event_contains=word, privacy='public', state='Published')
            elif location:
                results = get_paginated(__event_location=location, privacy='public', state='Published')
            elif word:
                results = get_paginated(__event_contains=word, privacy='public', state='Published')

        return self.render('/gentelella/guest/search/results.html',
                           results=results,
                           location=location,
                           filters=filters,
                           current_page=current_page)

def get_date_range(day_filter):
    pass
