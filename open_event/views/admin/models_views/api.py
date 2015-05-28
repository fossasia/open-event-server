from flask.ext.admin import BaseView, expose


class ApiView(BaseView):
    @expose('/')
    def index(self):
        return self.render('admin/api/index.html')
