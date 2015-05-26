from flask.ext.admin.contrib.sqla import ModelView


class SpeakerView(ModelView):
    column_list = ('name', 'email',)
