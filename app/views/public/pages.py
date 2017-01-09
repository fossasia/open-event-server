from flask import Blueprint
from flask import render_template
from flask import abort

from app.helpers.data_getter import DataGetter

pages = Blueprint('basicpagesview', __name__)


@pages.route('/<url>/', methods=('GET', 'POST'))
def url_view(url):
    from app import get_locale
    page = DataGetter.get_page_by_url('/' + url, get_locale())
    if page == None:
		return abort(404)
    return render_template('gentelella/guest/page.html', page=page)


@pages.route('/sitemap', methods=('GET', 'POST'))
def sitemap_view():
    return render_template('gentelella/guest/sitemap.html')
