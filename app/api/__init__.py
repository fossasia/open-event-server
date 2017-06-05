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
from app.api.image_sizes import ImageSizeList, ImageSizeDetail
from app.api.session_types import SessionTypeList, SessionTypeDetail, SessionTypeRelationship
from app.api.event_copyright import EventCopyrightList, EventCopyrightDetail, EventCopyrightRelationship


api_v1 = Blueprint('v1', __name__, url_prefix='/v1')
api = Api(app, api_v1)

# users
api.route(UserList, 'user_list', '/users')
api.route(UserDetail, 'user_detail', '/users/<int:id>', '/notifications/<int:notification_id>/user')
api.route(UserRelationship, 'user_notification', '/users/<int:id>/relationships/notifications')

# notifications
api.route(NotificationList, 'notification_list', '/notifications', '/users/<int:id>/notifications')
api.route(NotificationDetail, 'notification_detail', '/notifications/<int:id>')
api.route(NotificationRelationship, 'notification_user',
          '/notifications/<int:id>/relationships/user')

# image_sizes
api.route(ImageSizeList, 'image_size_list', '/image_sizes')
api.route(ImageSizeDetail, 'image_size_detail', '/image_sizes/<int:id>')

# tickets
api.route(AllTicketList, 'all_ticket_list', '/tickets', '/events/<int:id>/tickets')
api.route(TicketDetail, 'ticket_detail', '/tickets/<int:id>', '/events/<int:event_id>/tickets')
api.route(TicketRelationship, 'ticket_event', '/tickets/<int:id>/relationships/event')

# events
api.route(EventList, 'event_list', '/events')
api.route(EventDetail, 'event_detail', '/events/<int:id>', '/tickets/<int:ticket_id>/event',
          '/microlocations/<int:microlocation_id>/event', '/social_links/<int:social_link_id>/event',
          '/sponsors/<int:sponsor_id>/event', '/tracks/<int:track_id>/event',
          '/call_for_papers/<int:call_for_paper_id>/event', '/session_types/<int:session_type_id>/event',
          '/event_copyright/<int:copyright_id>/event')
api.route(EventRelationship, 'event_ticket', '/events/<int:id>/relationships/ticket')
api.route(EventRelationship, 'event_microlocation', '/events/<int:id>/relationships/microlocation')
api.route(EventRelationship, 'event_social_link', '/events/<int:id>/relationships/social_link')
api.route(EventRelationship, 'event_sponsor', '/events/<int:id>/relationships/sponsor')
api.route(EventRelationship, 'event_tracks', '/events/<int:id>/relationships/tracks')
api.route(EventRelationship, 'event_call_for_paper', '/events/<int:id>/relationships/call_for_paper')
api.route(EventRelationship, 'event_session_types', '/events/<int:id>/relationships/session_types')
api.route(EventRelationship, 'event_copyright', '/events/<int:id>/relationships/event_copyright')

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
api.route(SessionList, 'session_list', '/sessions', '/events/<int:id>/sessions', '/tracks/<int:track_id>/sessions',
          '/session_types/<int:session_type_id>/sessions')
api.route(SessionDetail, 'session_detail', '/sessions/<int:id>',
          '/microlocations/<int:microlocation_id>/sessions', '/events/<int:event_id>/microlocations')
api.route(SessionRelationship, 'session_microlocation',
          '/sessions/<int:id>/relationships/microlocation')
api.route(SessionRelationship, 'session_track', '/sessions/<int:id>/relationships/track')
api.route(SessionRelationship, 'session_session_type', '/sessions/<int:id>/relationships/session_type')

# social_links
api.route(SocialLinkList, 'social_link_list', '/events/<int:id>/social_links')
api.route(SocialLinkDetail, 'social_link_detail',
          '/social_links/<int:id>', '/events/<int:event_id>/social_links')
api.route(SocialLinkRelationship, 'social_link_event',
          '/social_links/<int:id>/relationships/event')

# sponsors
api.route(SponsorList, 'sponsor_list', '/sponsors', '/events/<int:event_id>/sponsors')
api.route(SponsorDetail, 'sponsor_detail', '/sponsors/<int:id>')
api.route(SponsorRelationship, 'sponsor_event', '/sponsors/<int:id>/relationships/event')

# tracks
api.route(TrackList, 'track_list', '/tracks', '/events/<int:event_id>/tracks')
api.route(TrackDetail, 'track_detail', '/tracks/<int:id>', '/sessions/<int:session_id>/track')
api.route(TrackRelationship, 'track_sessions', '/tracks/<int:id>/relationships/sessions')
api.route(TrackRelationship, 'track_event', '/tracks/<int:id>/relationships/event')

# call_for_papers
api.route(CallForPaperList, 'call_for_paper_list', '/events/<int:event_id>/call_for_papers')
api.route(CallForPaperDetail, 'call_for_paper_detail', '/call_for_papers/<int:id>',
          '/events/<int:event_id>/call_for_papers')
api.route(CallForPaperRelationship, 'call_for_paper_event', '/call_for_papers/<int:id>/relationships/event')

# session_types
api.route(SessionTypeList, 'session_type_list', '/events/<int:event_id>/session_types')
api.route(SessionTypeDetail, 'session_type_detail', '/session_types/<int:id>',
          '/sessions/<int:session_id>/session_type')
api.route(SessionTypeRelationship, 'session_type_sessions', '/session_types/<int:id>/relationships/sessions')
api.route(SessionTypeRelationship, 'session_type_event', '/session_types/<int:id>/relationships/event')

# event_copyright
api.route(EventCopyrightList, 'event_copyright_list', '/events/<int:id>/event_copyright')
api.route(EventCopyrightDetail, 'event_copyright_detail',
          '/event_copyright/<int:id>', '/events/<int:event_id>/event_copyright')
api.route(EventCopyrightRelationship, 'copyright_event',
          '/event_copyright/<int:id>/relationships/event')
