from math import ceil

from flask import url_for, render_template, make_response, request, \
    Blueprint, abort

from app.settings import get_settings
from app.helpers.data_getter import DataGetter
from app.models.event import Event
from app.models.setting import Environment

sitemaps = Blueprint('sitemaps', __name__)

# INDEX PAGES LIST

PER_PAGE_EVENTS = 500

event_details_pages = [
    'display_event_detail_home',
    'display_event_sessions',
    'display_event_schedule',
    'display_event_cfs',
    'display_event_coc'
]


@sitemaps.route('/sitemap.xml')
def render_sitemap():
    if get_settings()['app_environment'] == Environment.STAGING:
        urls = []
    else:
        urls = [full_url(url_for('sitemaps.render_pages_sitemap'))]
        # pages sitemap
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


@sitemaps.route('/sitemaps/pages.xml.gz')
def render_pages_sitemap():
    if get_settings()['app_environment'] == Environment.STAGING:
        abort(404)
    urls = [
        page.url if page.url.find('://') > -1 else
        full_url(url_for('basicpagesview.url_view', url=page.url))
        for page in DataGetter.get_all_pages()
        ]
    return make_sitemap_response(urls)


@sitemaps.route('/sitemaps/events/<int:num>.xml.gz')
def render_event_pages(num):
    if get_settings()['app_environment'] == Environment.STAGING:
        abort(404)
    main_urls = []
    start = (num - 1) * PER_PAGE_EVENTS
    end = PER_PAGE_EVENTS * num
    events = get_indexable_events()[start:end]
    if len(events) == 0:
        abort(404)

    for e in events:
        urls = [
            full_url(url_for('event_detail.' + view, identifier=e.identifier))
            for view in event_details_pages
            ]
        main_urls += urls
    return make_sitemap_response(main_urls)


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
