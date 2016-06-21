from flask_admin import BaseView, expose
from ...helpers.data_getter import DataGetter


class BrowseView(BaseView):
    @expose('/', methods=('GET', 'POST'))
    def browse(self, location):
        results = DataGetter.get_all_events()
        return self.render('/gentelella/guest/search/results.html', results=results, location=location)
