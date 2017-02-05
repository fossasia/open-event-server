from datetime import datetime

from flask import request

from app.helpers.babel import babel
from app.helpers.data_getter import DataGetter
from app.settings import get_settings
from config import LANGUAGES


@babel.localeselector
def get_locale():
    try:
        return request.cookies["selected_lang"]
    except:
        return request.accept_languages.best_match(LANGUAGES.keys())


def init_variables(app):
    @app.context_processor
    def template_context():
        return dict(
            all_languages=LANGUAGES,
            selected_lang=get_locale(),
            settings=get_settings(),
            app_name=get_settings()['app_name'],
            tagline=get_settings()['tagline'],
            event_typo=DataGetter.get_event_types()[:10],
            base_dir=app.config['BASE_DIR'],
            system_pages=DataGetter.get_all_pages(get_locale()),
            datetime_now=datetime.now(),
            logo=DataGetter.get_custom_placeholder_by_name('Logo'),
            avatar=DataGetter.get_custom_placeholder_by_name('Avatar'),
            integrate_socketio=app.config.get('INTEGRATE_SOCKETIO', False)
        )
