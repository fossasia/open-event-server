from flask import current_app as app, Blueprint
from flask_rest_jsonapi import Api
from app.api.users import UserList, UserDetail
from app.api.tickets import AllTicketList, TicketDetail, TicketRelationship
from app.api.events import EventList, EventDetail, EventRelationship
from app.api.microlocations import MicrolocationList, MicrolocationDetail, MicrolocationRelationship
from app.api.sessions import SessionList, SessionDetail, SessionRelationship


api_v1 = Blueprint('v1', __name__, url_prefix='/v1')
api = Api(app, api_v1)

# users
api.route(UserList, 'user_list', '/users')
api.route(UserDetail, 'user_detail', '/users/<int:id>')

# tickets
api.route(AllTicketList, 'all_ticket_list', '/tickets', '/events/<int:event_id>/tickets')
api.route(TicketDetail, 'ticket_detail', '/tickets/<int:id>')
api.route(TicketRelationship, 'ticket_event', '/tickets/<int:id>/relationships/event')

# events
api.route(EventList, 'event_list', '/events')
api.route(EventDetail, 'event_detail', '/events/<int:id>', '/tickets/<int:ticket_id>/event','/microlocations/<int:microlocation_id>/event')
api.route(EventRelationship, 'event_ticket', '/events/<int:id>/relationships/ticket')
api.route(EventRelationship, 'event_microlocation', '/events/<int:id>/relationships/microlocation')

# microlocations
api.route(MicrolocationList, 'microlocation_list', '/microlocations', '/events/<int:id>/microlocations', '/sessions/<int:id>/microlocations')
api.route(MicrolocationDetail, 'microlocation_detail', '/microlocations/<int:id>', '/sessions/<int:session_id>/microlocation', '/events/<int:event_id>/microlocation')
api.route(MicrolocationRelationship, 'microlocation_session', '/microlocations/<int:id>/relationships/session')
api.route(MicrolocationRelationship, 'microlocation_event', '/microlocations/<int:id>/relationships/event')

# sessions
api.route(SessionList, 'session_list', '/sessions', '/events/<int:id>/sessions')
api.route(SessionDetail, 'session_detail', '/sessions/<int:id>', '/microlocations/<int:microlocation_id>/sessions', '/events/<int:event_id>/microlocations')
api.route(SessionRelationship, 'session_microlocation', '/sessions/<int:id>/relationships/microlocation')
