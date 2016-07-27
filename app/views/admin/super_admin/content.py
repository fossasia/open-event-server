from flask_admin import expose
from super_admin_base import SuperAdminBaseView
from ....helpers.data_getter import DataGetter


class SuperAdminContentView(SuperAdminBaseView):
    @expose('/', methods=('GET', 'POST'))
    def index_view(self):
        pages = DataGetter.get_all_pages()
        return self.render(
            '/gentelella/admin/super_admin/content/content.html', pages=pages
        )
