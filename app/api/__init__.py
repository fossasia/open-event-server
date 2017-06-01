from flask import current_app as app, Blueprint
from flask_rest_jsonapi import Api

from app.api.users import UserList, UserDetail
from app.api.tickets import AllTicketList, TicketDetail, TicketRelationship
from app.api.events import EventList, EventDetail, EventRelationship
from app.api.microlocations import MicrolocationList, MicrolocationDetail, MicrolocationRelationship
from app.api.sessions import SessionList, SessionDetail, SessionRelationship
from app.api.social_links import SocialLinkList, SocialLinkDetail, SocialLinkRelationship
from app.api.sponsors import SponsorList, SponsorDetail, SponsorRelationship


api_v1 = Blueprint('v1', __name__, url_prefix='/v1')
api = Api(app, api_v1)

# users
api.route(UserList, 'user_list', '/users')
api.route(UserDetail, 'user_detail', '/users/<int:id>')

# tickets
api.route(AllTicketList, 'all_ticket_list', '/tickets', '/events/<int:id>/tickets')
api.route(TicketDetail, 'ticket_detail', '/tickets/<int:id>', '/events/<int:event_id>/tickets')
api.route(TicketRelationship, 'ticket_event', '/tickets/<int:id>/relationships/event')

# events
api.route(EventList, 'event_list', '/events')
api.route(EventDetail, 'event_detail', '/events/<int:id>', '/tickets/<int:ticket_id>/event',
          '/microlocations/<int:microlocation_id>/event', '/social_links/<int:social_link_id>/event',
          '/sponsors/<int:sponsor_id>/event')
api.route(EventRelationship, 'event_ticket', '/events/<int:id>/relationships/ticket')
api.route(EventRelationship, 'event_microlocation', '/events/<int:id>/relationships/microlocation')
api.route(EventRelationship, 'event_social_link', '/events/<int:id>/relationships/social_link')
api.route(EventRelationship, 'event_sponsor', '/events/<int:id>/relationships/sponsor')

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
api.route(SessionList, 'session_list', '/sessions', '/events/<int:id>/sessions')
api.route(SessionDetail, 'session_detail', '/sessions/<int:id>',
          '/microlocations/<int:microlocation_id>/sessions', '/events/<int:event_id>/microlocations')
api.route(SessionRelationship, 'session_microlocation',
          '/sessions/<int:id>/relationships/microlocation')

# social_links
api.route(SocialLinkList, 'social_link_list', '/social_links', '/events/<int:id>/social_links')
api.route(SocialLinkDetail, 'social_link_detail',
          '/social_links/<int:id>', '/events/<int:event_id>/social_links')
api.route(SocialLinkRelationship, 'social_link_event',
          '/social_links/<int:id>/relationships/event')

#sponsors
api.route(SponsorList, 'sponsor_list', '/sponsors', '/events/<int:event_id>/sponsors')
api.route(SponsorDetail, 'sponsor_detail', '/sponsors/<int:id>', '/events/<int:event_id>/sponsors/<int:id>')
api.route(SponsorRelationship, 'sponsor_event', '/sponsors/<int:id>/relationships/event')

