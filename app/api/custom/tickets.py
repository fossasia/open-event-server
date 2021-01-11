from flask import Blueprint, jsonify

from app.api.attendees import get_sold_and_reserved_tickets_count
from app.models.ticket import Ticket

tickets_routes = Blueprint('tickets_routes', __name__, url_prefix='/v1/events')


@tickets_routes.route('/<int:event_id>/tickets/availability')
def get_stock(event_id):
    stock = []
    availability = {}
    tickets = Ticket.query.filter_by(event_id=event_id).all()
    for i in tickets:
        total_count = i.quantity - get_sold_and_reserved_tickets_count(i.id)
        availability["id"] = i.id
        availability["name"] = i.name
        availability["quantity"] = i.quantity
        availability["available"] = total_count
        stock.append(availability.copy())

    print(stock)
    return jsonify(stock)
