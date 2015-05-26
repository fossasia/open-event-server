from flask.ext.admin.contrib.sqla import ModelView


class SponsorView(ModelView):
    column_list = ('name',)