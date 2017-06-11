from flask import Blueprint
from flask import url_for, redirect

from app.helpers.data import delete_from_db
from app.helpers.data_getter import DataGetter
from app.helpers.permission_decorators import *

event_sponsors = Blueprint('event_sponsors', __name__, url_prefix='/events/<int:event_id>/sponsors')


@event_sponsors.route('/<sponsor_id>/delete/')
@can_access
def delete_view(event_id, sponsor_id):
    sponsor = DataGetter.get_sponsor(sponsor_id)
    delete_from_db(sponsor, "Sponsor deleted")
    return redirect(url_for('events.details_view', event_id=event_id))
