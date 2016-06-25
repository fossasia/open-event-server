from flask_admin import BaseView, expose
from ...helpers.data_getter import DataGetter
from flask import request
import requests
from urlparse import urlparse
from flask_restplus import marshal
from open_event.api.events import DAO as EventDAO, EVENT


class BrowseView(BaseView):
    @expose('/', methods=('GET', 'POST'))
    def browse(self, location):
        results = DataGetter.get_all_events()
        return self.render('/gentelella/guest/search/results.html', results=results, location=location)

    @expose('/s', methods=('GET', 'POST'))
    def browses(self, location):
        results = marshal(EventDAO.list(location_name=location, privacy='public', state='Published'), EVENT)
        if request.method == "POST":
            word = request.form['word']
            event_type = request.args.get('event_type', '')
            if location and word and event_type:
                results = marshal(
                    EventDAO.list(location_name=location,
                                  __event_contains=word,
                                  privacy='public',
                                  state='Published',
                                  type=event_type),
                    EVENT)
            if location and word:
                results = marshal(EventDAO.list(location_name=location, __event_contains=word, privacy='public', state='Published'), EVENT)
            elif location:
                results = marshal(EventDAO.list(location_name=location, privacy='public', state='Published'), EVENT)
            elif word:
                results = marshal(EventDAO.list(__event_contains=word, privacy='public', state='Published'), EVENT)
            return self.render('/gentelella/guest/search/results.html', results=results, location=location)
        return self.render('/gentelella/guest/search/results.html', results=results, location=location)

