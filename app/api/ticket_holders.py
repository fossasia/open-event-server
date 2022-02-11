from app.api.helpers.db import safe_query_kwargs
from app.api.helpers.errors import ForbiddenError
from app.api.helpers.permission_manager import has_access
from app.models.ticket_holder import TicketHolder
from app.models.user import User
from app.models import db
from app.api.schema.ticket_holders import TicketHolderSchema

from flask import Blueprint, current_app, jsonify, redirect, request, url_for
from flask_jwt_extended import current_user
from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from app.api.helpers.permissions import jwt_required

ticket_holder_routes = Blueprint('ticket_holder_misc', __name__, url_prefix='/v1')

class TicketHolderList(ResourceList):
  """
  TickerHolderList class for TicketHolder schema
  """

  def query(self, view_kwargs):
    query_ = self.session.query(TicketHolder)
    # tickets under a user
    user = safe_query_kwargs(User, view_kwargs)
    if not has_access('is_user_itself', user_id=user.id):
      raise ForbiddenError({'source': 'user_id'}, 'Access Forbidden')
    query_ = query_.filter(TicketHolder.email == user.email)
    return query_
  
  decorators = (jwt_required,)
  schema = TicketHolderSchema
  data_layer = {
    'session': db.session,
    'model': TicketHolder
  }
  methods = [
    'GET',
  ]