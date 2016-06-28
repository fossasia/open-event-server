from flask import url_for, render_template, make_response, request, \
    Blueprint

from open_event.models.event import Event

app = Blueprint('sitemaps', __name__)


@app.route('/sitemap.xml', methods=('GET', 'POST'))
def render_sitemap():
    events = Event.query.filter_by(privacy='public').all()
    urls = [
        request.url_root.strip('/') +
        url_for('event_detail.display_event_detail_home', event_id=e.id)
        for e in events
    ]
    sitemap = render_template('sitemap/sitemap.xml', urls=urls)
    resp = make_response(sitemap)
    resp.headers['Content-Type'] = 'application/xml'
    return resp
