from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Relationship, Schema

from app.api.helpers.utilities import dasherize
from app.api.schema.base import GetterRelationship
from app.models import db
from utils.common import use_defaults

class TicketHolderSchema(Schema):
  class Meta:
    type_ = 'ticket-holder'
    self_view = 'v1.ticket_holder_list'
    self_view_kwargs = {'id': '<id>'}
  
  id = fields.Str(dump_only=True)
  firstname = fields.Str()
  lastname = fields.Str()
  email = fields.Str()
  address = fields.Str()
  city = fields.Str()
  state = fields.Str()
  country = fields.Str()
  job_title = fields.Str()
  phone = fields.Str()
  tax_business_info = fields.Str()
  billing_address = fields.Str()
  home_address = fields.Str()
  shipping_address = fields.Str()
  company = fields.Str()
  work_address = fields.Str()
  work_phone = fields.Str()
  website = fields.Str()
  blog = fields.Str()
  twitter = fields.Str()
  facebook = fields.Str()
  instagram = fields.Str()
  linkedin = fields.Str()
  github = fields.Str()
  gender = fields.Str()
  accept_video_recording = fields.Boolean()
  accept_share_details = fields.Boolean()
  accept_recieve_details = fields.Boolean()
  age_group = fields.Str()
  birth_date = fields.DateTime()
  pdf_url = fields.Str()
  created_at = fields.DateTime()
  modified_at = fields.DateTime()

  # user = Relationship(
  #   self_view='v1.ticket_holder_list',
  #   self_view_kwargs={'id': '<id>'},
  #   related_view='v1.user_detail',
  #   schema='UserSchemaPublic',
  #   related_view_kwargs={'ticket_holder_id': '<id>'},
  #   type_='user',
  # )
