from flask import current_app as app, Blueprint
from flask_rest_jsonapi import Api

from app.api.users import UserList, UserDetail, UserRelationship
from app.api.notifications import NotificationList, NotificationDetail, NotificationRelationship
from app.api.tickets import AllTicketList, TicketDetail, TicketRelationship
from app.api.events import EventList, EventDetail, EventRelationship
from app.api.microlocations import MicrolocationList, MicrolocationDetail, MicrolocationRelationship
from app.api.sessions import SessionList, SessionDetail, SessionRelationship
from app.api.social_links import SocialLinkList, SocialLinkDetail, SocialLinkRelationship
from app.api.sponsors import SponsorList, SponsorDetail, SponsorRelationship
from app.api.tracks import TrackList, TrackDetail, TrackRelationship
from app.api.call_for_papers import CallForPaperList, CallForPaperDetail, CallForPaperRelationship
from app.api.event_invoices import EventInvoiceList, EventInvoiceDetail, EventInvoiceRelationship
from app.api.image_sizes import ImageSizeList, ImageSizeDetail
from app.api.session_types import SessionTypeList, SessionTypeDetail, SessionTypeRelationship
from app.api.event_copyright import EventCopyrightList, EventCopyrightDetail, EventCopyrightRelationship
from app.api.pages import PageList, PageDetail
from app.api.tax import TaxList, TaxDetail,TaxRelationship

api_v1 = Blueprint('v1', __name__, url_prefix='/v1')
api = Api(app, api_v1)

# users
api.route(UserList, 'user_list', '/users')
api.route(UserDetail, 'user_detail', '/users/<int:id>', '/notifications/<int:notification_id>/user', '/event-invoices/<int:event_invoice_id>/user')
api.route(UserRelationship, 'user_notification', '/users/<int:id>/relationships/notifications')
api.route(UserRelationship, 'user_event_invoices', '/users/<int:id>/relationships/event-invoices')

# notifications
api.route(NotificationList, 'notification_list', '/notifications', '/users/<int:id>/notifications')
api.route(NotificationDetail, 'notification_detail', '/notifications/<int:id>')
api.route(NotificationRelationship, 'notification_user',
          '/notifications/<int:id>/relationships/user')

# image_sizes
api.route(ImageSizeList, 'image_size_list', '/image-sizes')
api.route(ImageSizeDetail, 'image_size_detail', '/image-sizes/<int:id>')

# pages
api.route(PageList, 'page_list', '/pages')
api.route(PageDetail, 'page_detail', '/pages/<int:id>')

# tickets
api.route(AllTicketList, 'all_ticket_list', '/tickets', '/events/<int:id>/tickets')
api.route(TicketDetail, 'ticket_detail', '/tickets/<int:id>', '/events/<int:event_id>/tickets')
api.route(TicketRelationship, 'ticket_event', '/tickets/<int:id>/relationships/event')

# events
api.route(EventList, 'event_list', '/events')
api.route(EventDetail, 'event_detail', '/events/<int:id>', '/tickets/<int:ticket_id>/event',
          '/microlocations/<int:microlocation_id>/event', '/social-links/<int:social_link_id>/event',
          '/sponsors/<int:sponsor_id>/event', '/tracks/<int:track_id>/event',
          '/call-for-papers/<int:call_for_paper_id>/event', '/session-types/<int:session_type_id>/event',
          '/event-copyright/<int:copyright_id>/event', '/tax/<int:tax_id>/event', '/event-invoices/<int:event_invoice_id>/event')
api.route(EventRelationship, 'event_ticket', '/events/<int:id>/relationships/ticket')
api.route(EventRelationship, 'event_microlocation', '/events/<int:id>/relationships/microlocation')
api.route(EventRelationship, 'event_social_link', '/events/<int:id>/relationships/social-link')
api.route(EventRelationship, 'event_sponsor', '/events/<int:id>/relationships/sponsor')
api.route(EventRelationship, 'event_tracks', '/events/<int:id>/relationships/tracks')
api.route(EventRelationship, 'event_call_for_paper', '/events/<int:id>/relationships/call-for-paper')
api.route(EventRelationship, 'event_session_types', '/events/<int:id>/relationships/session-types')
api.route(EventRelationship, 'event_copyright', '/events/<int:id>/relationships/event-copyright')
api.route(EventRelationship, 'event_tax', '/events/<int:id>/relationships/tax')
api.route(EventRelationship, 'event_event_invoice', '/events/<int:id>/relationships/event-invoices')

# microlocations
api.route(MicrolocationList, 'microlocation_list', '/microlocations',
          '/events/<int:id>/microlocations', '/sessions/<int:id>/microlocations')
api.route(MicrolocationDetail, 'microlocation_detail', '/microlocations/<int:id>',
          '/sessions/<int:session_id>/microlocation', '/events/<int:event_id>/microlocation')
api.route(MicrolocationRelationship, 'microlocation_session',
          '/microlocations/<int:id>/relationships/session')
api.route(MicrolocationRelationship, 'microlocation_event',
          '/microlocations/<int:id>/relationships/event')

# sessions
api.route(SessionList, 'session_list', '/events/<int:id>/sessions', '/tracks/<int:track_id>/sessions',
          '/session-types/<int:session_type_id>/sessions', '/microlocations/<int:microlocation_id>/sessions')
api.route(SessionDetail, 'session_detail', '/sessions/<int:id>', '/events/<int:event_id>/microlocations')
api.route(SessionRelationship, 'session_microlocation',
          '/sessions/<int:id>/relationships/microlocation')
api.route(SessionRelationship, 'session_track', '/sessions/<int:id>/relationships/track')
api.route(SessionRelationship, 'session_session_type', '/sessions/<int:id>/relationships/session-type')

# social_links
api.route(SocialLinkList, 'social_link_list', '/events/<int:id>/social-links')
api.route(SocialLinkDetail, 'social_link_detail',
          '/social-links/<int:id>', '/events/<int:event_id>/social-links')
api.route(SocialLinkRelationship, 'social_link_event',
          '/social-links/<int:id>/relationships/event')

# sponsors
api.route(SponsorList, 'sponsor_list', '/sponsors', '/events/<int:event_id>/sponsors')
api.route(SponsorDetail, 'sponsor_detail', '/sponsors/<int:id>')
api.route(SponsorRelationship, 'sponsor_event', '/sponsors/<int:id>/relationships/event')

# tracks
api.route(TrackList, 'track_list', '/events/<int:event_id>/tracks')
api.route(TrackDetail, 'track_detail', '/tracks/<int:id>', '/sessions/<int:session_id>/track')
api.route(TrackRelationship, 'track_sessions', '/tracks/<int:id>/relationships/sessions')
api.route(TrackRelationship, 'track_event', '/tracks/<int:id>/relationships/event')

# call_for_papers
api.route(CallForPaperList, 'call_for_paper_list', '/events/<int:event_id>/call-for-papers')
api.route(CallForPaperDetail, 'call_for_paper_detail', '/call-for-papers/<int:id>',
          '/events/<int:event_id>/call-for-papers')
api.route(CallForPaperRelationship, 'call_for_paper_event', '/call-for-papers/<int:id>/relationships/event')

# session_types
api.route(SessionTypeList, 'session_type_list', '/events/<int:event_id>/session-types')
api.route(SessionTypeDetail, 'session_type_detail', '/session-types/<int:id>',
          '/sessions/<int:session_id>/session-type')
api.route(SessionTypeRelationship, 'session_type_sessions', '/session-types/<int:id>/relationships/sessions')
api.route(SessionTypeRelationship, 'session_type_event', '/session-types/<int:id>/relationships/event')

# event_copyright
api.route(EventCopyrightList, 'event_copyright_list', '/events/<int:id>/event-copyright')
api.route(EventCopyrightDetail, 'event_copyright_detail',
          '/event-copyright/<int:id>', '/events/<int:event_id>/event-copyright')
api.route(EventCopyrightRelationship, 'copyright_event',
          '/event-copyright/<int:id>/relationships/event')

# tax
api.route(TaxList, 'tax_list', '/events/<int:id>/tax')
api.route(TaxDetail, 'tax_detail', '/tax/<int:id>', '/events/<int:event_id>/tax')
api.route(TaxRelationship, 'tax_event','/tax/<int:id>/relationships/event')

# event invoices
api.route(EventInvoiceList, 'event_invoice_list', '/events/<int:event_id>/event-invoices',
          '/users/<int:user_id>/event-invoices')
api.route(EventInvoiceDetail, 'event_invoice_detail', '/event-invoices/<int:id>')
api.route(EventInvoiceRelationship, 'event_invoice_user', '/event-invoices/<int:id>/relationships/user')
api.route(EventInvoiceRelationship, 'event_invoice_event', '/event-invoices/<int:id>/relationships/event')
