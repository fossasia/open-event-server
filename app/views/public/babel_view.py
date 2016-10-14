from app.helpers.babel import babel
from flask import request, Blueprint
from config import LANGUAGES


app = Blueprint('babel', __name__)

@app.route('/choose_language', methods=('POST',))
def set_lang():
    global selected_lang
    l_code = request.form.get('l_code')
    if l_code:
        selected_lang = l_code
    return selected_lang

@babel.localeselector
def get_locale():
    try:
        return selected_lang
    except:
        return request.accept_languages.best_match(LANGUAGES.keys())