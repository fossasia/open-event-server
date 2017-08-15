from flask_rest_jsonapi import ResourceDetail, ResourceList

from app.api.bootstrap import api
from app.api.schema.pages import PageSchema
from app.models import db
from app.models.page import Page


class PageList(ResourceList):
    """
    List and create page
    """
    decorators = (api.has_permission('is_admin', methods="POST"),)
    schema = PageSchema
    data_layer = {'session': db.session,
                  'model': Page}


class PageDetail(ResourceDetail):
    """
    Page detail by id
    """
    schema = PageSchema
    decorators = (api.has_permission('is_admin', methods="PATCH,DELETE"),)
    data_layer = {'session': db.session,
                  'model': Page}
