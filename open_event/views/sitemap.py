from flask import url_for, render_template, make_response, request, \
    Blueprint
from math import ceil

from open_event.models.event import Event

app = Blueprint('sitemaps', __name__)

# INDEX PAGES LIST

PER_PAGE_EVENTS = 500

event_details_pages = [
    'display_event_detail_home',
    'display_event_sessions',
    'display_event_schedule',
    'display_event_cfs',
    'display_event_coc'
]

static_pages = [
    'how_it_works',
    'pricing',
    'about'
]


@app.route('/sitemap.xml', methods=('GET', 'POST'))
def render_sitemap():
    urls = []
    # pages sitemap
    urls.append(
        full_url(url_for('sitemaps.render_pages_sitemap'))
    )
    # get events pages
    events = get_indexable_events()
    pages = int(ceil(len(events) / (PER_PAGE_EVENTS * 1.0)))
    for num in range(1, pages + 1):
        urls.append(
            full_url(url_for('sitemaps.render_event_pages', num=num))
        )
    # make sitemap
    sitemap = render_template('sitemap/sitemap_index.xml', sitemaps=urls)
    resp = make_response(sitemap)
    resp.headers['Content-Type'] = 'application/xml'
    return resp


@app.route('/sitemaps/pages.xml.gz', methods=('GET', 'POST'))
def render_pages_sitemap():
    urls = [
        full_url(url_for('basicpagesview.' + page)) for page in static_pages
    ]
    return make_sitemap_response(urls)


@app.route('/sitemaps/events/<int:num>.xml.gz', methods=('GET', 'POST'))
def render_event_pages(num):
    main_urls = []
    start = (num - 1) * PER_PAGE_EVENTS
    end = PER_PAGE_EVENTS * num
    events = get_indexable_events()[start:end]

    for e in events:
        urls = [
            full_url(url_for('event_detail.' + view, event_id=e.id))
            for view in event_details_pages
        ]
        main_urls += urls
    return make_sitemap_response(urls)

##########
# Helpers
##########


def make_sitemap_response(urls):
    sitemap = render_template('sitemap/sitemap.xml', urls=urls)
    resp = make_response(sitemap)
    resp.headers['Content-Type'] = 'application/xml'
    return resp


def get_indexable_events():
    events = Event.query.filter_by(privacy='public').order_by('id')
    return list(events)


def full_url(url):
    return request.url_root.strip('/') + url
