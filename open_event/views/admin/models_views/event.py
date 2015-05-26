from flask.ext.admin.contrib.sqla import ModelView


class EventView(ModelView):
    column_list = ('name', 'location_name',)