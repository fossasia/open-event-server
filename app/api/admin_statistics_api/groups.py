from flask_rest_jsonapi import ResourceDetail
from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Schema

from app.api.bootstrap import api
from app.api.data_layers.NoModelLayer import NoModelLayer
from app.api.helpers.utilities import dasherize
from app.models import db
from app.models.event import Event
from app.models.group import Group
from app.models.user_follow_group import UserFollowGroup


class AdminStatisticsGroupSchema(Schema):
    """
    Api schema
    """

    class Meta:
        """
        Meta class
        """

        type_ = 'admin-statistics-group'
        self_view = 'v1.admin_statistics_group_detail'
        inflect = dasherize

    id = fields.String()
    groups = fields.Method("number_of_groups")
    group_events = fields.Method("number_of_group_events")
    followers = fields.Method("number_of_followers")

    def number_of_groups(self, obj):
        all_group = db.session.query(Group).all()
        return len(all_group)

    def number_of_group_events(self, obj):
        unique_group = Event.query.filter(Event.group_id.isnot(None)).all()
        return len(unique_group)

    def number_of_followers(self, obj):
        unique_follower = db.session.query(UserFollowGroup.user_id).distinct()
        return unique_follower.count()


class AdminStatisticsGroupDetail(ResourceDetail):
    """
    Detail by id
    """

    methods = ['GET']
    decorators = (api.has_permission('is_admin'),)
    schema = AdminStatisticsGroupSchema
    data_layer = {'class': NoModelLayer, 'session': db.session}
