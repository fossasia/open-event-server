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
        results = DataGetter.get_all_events()
        if request.method == "POST":
            url = urlparse(request.url)
            word = request.form['word']
            if location and word:
                results = marshal(EventDAO.list(location_name=location, __event_contains=word), EVENT)
            elif location:
                results = marshal(EventDAO.list(location_name=location), EVENT)
            elif word:
                results = marshal(EventDAO.list(__event_contains=word), EVENT)
            return self.render('/gentelella/guest/search/results.html', results=results, location=location)
        return self.render('/gentelella/guest/search/results.html', results=results, location=location)

