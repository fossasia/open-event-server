from flask.ext.restplus import Namespace

from app.models.notifications import Notification as NotificationModel
from app.helpers.data import DataManager
from app.helpers.data_getter import DataGetter
from .helpers.helpers import (
    can_create,
    requires_auth
)
from .helpers.utils import PAGINATED_MODEL, ServiceDAO, \
     POST_RESPONSES
from .helpers.utils import Resource
from .helpers import custom_fields as fields

api = Namespace('notifications', description='Notifications', path='/')

NOTIFICATION = api.model('Notification', {
    'id': fields.Integer(required=True),
    'user_id': fields.Integer(required=True),
    'title': fields.String(),
    'message': fields.String(),
    'action': fields.String(),
    'received_at': fields.DateTime(),
})

NOTIFICATION_PAGINATED = api.clone('NotificationPaginated', PAGINATED_MODEL, {
    'results': fields.List(fields.Nested(NOTIFICATION))
})

NOTIFICATION_POST = api.clone('NotificationPost', NOTIFICATION)
del NOTIFICATION_POST['id']


# Create DAO
class NotificationDAO(ServiceDAO):
    version_key = 'notifications_ver'

    def create_user_notify(self, payload):
        user = DataGetter.get_user(payload['user_id'])
        DataManager().create_user_notification(user, payload['action'], payload['title'], payload['message'])
        return user

DAO = NotificationDAO(NotificationModel, NOTIFICATION_POST)


@api.route('/events/<int:event_id>/notifications')
class UserNotifications(Resource):

    @requires_auth
    @can_create(DAO)
    @api.doc('create_user_notification', responses=POST_RESPONSES)
    @api.marshal_with(NOTIFICATION)
    @api.expect(NOTIFICATION_POST)
    def post(self, event_id):
        """Create user notification"""
        return DAO.create_user_notify(
            self.api.payload,
        ), 201
