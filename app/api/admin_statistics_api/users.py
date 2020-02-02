from flask_rest_jsonapi import ResourceDetail
from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Schema

from app.api.bootstrap import api
from app.api.data_layers.NoModelLayer import NoModelLayer
from app.api.helpers.db import get_count
from app.api.helpers.utilities import dasherize
from app.models import db
from app.models.role import Role
from app.models.ticket_holder import TicketHolder
from app.models.user import User
from app.models.users_events_role import UsersEventsRoles


class AdminStatisticsUserSchema(Schema):
    """
    Api schema
    """

    class Meta:
        """
        Meta class
        """

        type_ = 'admin-statistics-user'
        self_view = 'v1.admin_statistics_user_detail'
        inflect = dasherize

    id = fields.String()
    super_admin = fields.Method("super_admin_count")
    admin = fields.Method("admin_count")
    verified = fields.Method("verified_count")
    unverified = fields.Method("unverified_count")
    owner = fields.Method("owner_count")
    organizer = fields.Method("organizer_count")
    coorganizer = fields.Method("coorganizer_count")
    attendee = fields.Method("attendee_count")
    track_organizer = fields.Method("track_organizer_count")

    def super_admin_count(self, obj):
        return get_count(User.query.filter_by(is_super_admin=True))

    def admin_count(self, obj):
        return get_count(User.query.filter_by(is_admin=True, is_super_admin=False))

    def verified_count(self, obj):
        return get_count(
            User.query.filter_by(is_verified=True, is_super_admin=False, is_admin=False)
        )

    def unverified_count(self, obj):
        return get_count(
            User.query.filter_by(is_verified=False, is_super_admin=False, is_admin=False)
        )

    def get_all_user_roles(self, role_name):
        role = Role.query.filter_by(name=role_name).first()
        newquery = (
            User.query.join(UsersEventsRoles.user)
            .join(UsersEventsRoles.role)
            .filter(UsersEventsRoles.role == role)
            .distinct()
        )
        return newquery

    def owner_count(self, obj):
        return self.get_all_user_roles('owner').count()

    def organizer_count(self, obj):
        return self.get_all_user_roles('organizer').count()

    def coorganizer_count(self, obj):
        return self.get_all_user_roles('coorganizer').count()

    def track_organizer_count(self, obj):
        return self.get_all_user_roles('track_organizer').count()

    def attendee_count(self, obj):
        unique_attendee_query = db.session.query(TicketHolder.email).distinct()
        return unique_attendee_query.count()


class AdminStatisticsUserDetail(ResourceDetail):
    """
    Detail by id
    """

    methods = ['GET']
    decorators = (api.has_permission('is_admin'),)
    schema = AdminStatisticsUserSchema
    data_layer = {'class': NoModelLayer, 'session': db.session}
