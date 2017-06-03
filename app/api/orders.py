from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Schema, Relationship
from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship

from app.api.helpers.permissions import jwt_required
from app.models import db
from app.models.order import Order
from app.models.event import Event


class OrderSchema(Schema):

    class Meta:
        type_ = 'order'
        self_view = 'v1.order_detail'
        self_view_kwargs = {'id': '<id>'}

    id = fields.Str(dump_only=True)
    status = fields.boolean()

    event = Relationship(attribute='event',
                         self_view='v1.order_event',
                         self_view_kwargs={'id': '<id>'},
                         related_view='v1.event_detail',
                         related_view_kwargs={'id': '<id>'},
                         schema='EventSchema',
                         type_='event')
    user = Relationship(attribute='user',
                         self_view='v1.order_user',
                         self_view_kwargs={'id': '<id>'},
                         related_view='v1.user_detail',
                         related_view_kwargs={'id': '<id>'},
                         schema='EventSchema',
                         type_='event')


class OrderList(ResourceList):

    def query(self, view_kwargs):
        query_ = self.session.query(Sponsor)
        if view_kwargs.get('event_id') is not None:
            query_ = query_.filter_by(event_id=view_kwargs['event_id'])
        if view_kwargs.get('user_id') is not None:
            query_ = query_.filter_by(user_id=view_kwargs['user_id'])
        return query_

    def before_create_object(self, data, view_kwargs):
        if view_kwargs.get('event_id') is not None:
            event = self.session.query(Event).filter_by(id=view_kwargs['event_id']).one()
            data['event_id'] = event.id
        if view_kwargs.get('order_id') is not None:
            order = self.session.query(Order).filter_by(id=view_kwargs['order_id']).one()
            data['order_id'] = order.id

    decorators = (jwt_required, can_access_orders, )
    schema = OrderSchema
    data_layer = {'session': db.session,
                  'model': Order,
                  'methods': {
                      'query': query,
                      'before_create_object': before_create_object
                  }}


class OrderRelationship(ResourceRelationship):

    decorators = (jwt_required, )
    schema = OrderSchema
    data_layer = {'session': db.session,
                  'model': Order}


class OrderDetail(ResourceDetail):
    """
    Order Detail by id
    """
    decorators = (jwt_required, can_access_orders, )
    schema = OrderSchema
    data_layer = {'session': db.session,
                  'model': Order}
