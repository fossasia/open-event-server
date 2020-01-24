from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from flask_rest_jsonapi import ResourceDetail
from sqlalchemy.sql import text

from app.api.bootstrap import api
from app.api.data_layers.NoModelLayer import NoModelLayer
from app.api.schema.admin_statistics_schema.events import AdminStatisticsEventSchema
from app.models import db

event_statistics = Blueprint(
    'event_statistics', __name__, url_prefix='/v1/admin/statistics'
)


@event_statistics.route('/event-topics', methods=['GET'])
@jwt_required
def event_topic_count():
    result_set = db.engine.execute(
        text(
            "SELECT event_topics.name AS name, event_topics.id AS id, "
            + "COUNT(events.id) AS count FROM event_topics "
            + "LEFT JOIN events ON events.event_topic_id = event_topics.id "
            + "GROUP BY event_topics.id;"
        )
    )
    event_topics_counts = [dict(each) for each in list(result_set)]
    return jsonify(event_topics_counts)


@event_statistics.route('/event-types', methods=['GET'])
@jwt_required
def event_types_count():
    result_set = db.engine.execute(
        text(
            "SELECT event_types.name AS name, event_types.id AS id, "
            + "COUNT(events.id) AS count FROM event_types "
            + "LEFT JOIN events ON events.event_type_id = event_types.id "
            + "GROUP BY event_types.id;"
        )
    )
    event_types_counts = [dict(each) for each in list(result_set)]
    return jsonify(event_types_counts)


class AdminStatisticsEventDetail(ResourceDetail):
    """
    Detail by id
    """

    methods = ['GET']
    decorators = (api.has_permission('is_admin'),)
    schema = AdminStatisticsEventSchema
    data_layer = {'class': NoModelLayer, 'session': db.session}
