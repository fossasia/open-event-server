from flask_admin import BaseView, expose
from ...helpers.data_getter import DataGetter


class BasicPagesView(BaseView):
    @expose('/', methods=('GET', 'POST'))
    def index(self):
        pass

    @expose('/<url>', methods=('GET', 'POST'))
    def url_view(self, url):
        page = DataGetter.get_page_by_url('/' + url)
        return self.render('/gentelella/guest/page.html', page=page)

    @expose('/sitemap', methods=('GET', 'POST'))
    def sitemap_view(self):
        return self.render('/gentelella/guest/sitemap.html')
