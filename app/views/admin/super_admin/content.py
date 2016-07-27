from flask_admin import expose
from super_admin_base import SuperAdminBaseView


class SuperAdminContentView(SuperAdminBaseView):
    @expose('/', methods=('GET', 'POST'))
    def index_view(self):
        return self.render(
            '/gentelella/admin/super_admin/content/content.html',
        )
