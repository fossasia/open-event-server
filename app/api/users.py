from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from marshmallow_jsonapi.flask import Schema, Relationship
from marshmallow_jsonapi import fields
from sqlalchemy.orm.exc import NoResultFound
from flask_rest_jsonapi.exceptions import ObjectNotFound

from app.models import db
from app.models.user import User
from app.models.notification import Notification
from app.models.import_job import ImportJob
from app.api.helpers.permissions import is_admin, is_user_itself, jwt_required


class UserSchema(Schema):
    """
    Api schema for User Model
    """
    class Meta:
        """
        Meta class for User Api Schema
        """
        type_ = 'user'
        self_view = 'v1.user_detail'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'v1.user_list'

    id = fields.Str(dump_only=True)
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True)
    avatar = fields.Str()
    is_super_admin = fields.Boolean(dump_only=True)
    is_admin = fields.Boolean(dump_only=True)
    is_verified = fields.Boolean(dump_only=True)
    signup_at = fields.DateTime(dump_only=True)
    last_accessed_at = fields.DateTime(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    deleted_at = fields.DateTime(dump_only=True)
    firstname = fields.Str()
    lastname = fields.Str()
    details = fields.Str()
    contact = fields.Str()
    facebook = fields.Str()
    twitter = fields.Str()
    instagram = fields.Str()
    google = fields.Str()
    avatar_uploaded = fields.Str()
    thumbnail = fields.Str()
    small = fields.Str()
    icon = fields.Str()
    notification = Relationship(
        attribute='notification',
        self_view='v1.user_notification',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.notification_list',
        related_view_kwargs={'user_id': '<id>'},
        schema='NotificationSchema',
        many=True,
        type_='notification'
    )
    import_jobs = Relationship(
        attribute='import_jobs',
        self_view='v1.user_import_jobs',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.import_job_list',
        related_view_kwargs={'user_id': '<id>'},
        schema='ImportJobSchema',
        many=True,
        type_='import_job'
    )


class UserList(ResourceList):
    """
    List and create Users
    """
    get = is_admin(ResourceList.get.__func__)
    schema = UserSchema
    data_layer = {'session': db.session,
                  'model': User}


class UserDetail(ResourceDetail):
    """
    User detail by id
    """
    def before_get_object(self, view_kwargs):
        if view_kwargs.get('notification_id') is not None:
            try:
                notification = self.session.query(Notification).filter_by(id=view_kwargs['notification_id']).one()
            except NoResultFound:
                raise ObjectNotFound({'parameter': 'notification_id'},
                                     "Notification: {} not found".format(view_kwargs['notification_id']))
            else:
                if notification.user_id is not None:
                    view_kwargs['id'] = notification.user_id
                else:
                    view_kwargs['id'] = None
        if view_kwargs.get('import_job_id') is not None:
            try:
                import_job = self.session.query(ImportJob).filter_by(id=view_kwargs['import_job_id']).one()
            except NoResultFound:
                raise ObjectNotFound({'parameter': 'import_job_id'},
                                     "ImportJob: {} not found".format(view_kwargs['import_job_id']))
            else:
                if import_job.user_id is not None:
                    view_kwargs['id'] = import_job.user_id
                else:
                    view_kwargs['id'] = None

    decorators = (is_user_itself, )
    schema = UserSchema
    data_layer = {'session': db.session,
                  'model': User,
                  'methods': {'before_get_object': before_get_object}}


class UserRelationship(ResourceRelationship):
    decorators = (jwt_required,)
    schema = UserSchema
    data_layer = {'session': db.session,
                  'model': User}
