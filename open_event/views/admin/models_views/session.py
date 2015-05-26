from flask.ext.admin.contrib.sqla import ModelView


class SessionView(ModelView):
    column_list = ('title', 'subtitle',)