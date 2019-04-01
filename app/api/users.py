import base64

from flask import Blueprint, request, jsonify, abort, make_response
from flask_jwt import current_identity as current_user
from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from sqlalchemy.orm.exc import NoResultFound
import urllib.error

from app import get_settings
from app.api.bootstrap import api
from app.api.helpers.db import safe_query, get_count
from app.api.helpers.exceptions import ConflictException, UnprocessableEntity, ForbiddenException
from app.api.helpers.files import create_save_image_sizes, make_frontend_url
from app.api.helpers.mail import send_email_confirmation, send_email_change_user_email, send_email_with_action
from app.api.helpers.permission_manager import has_access
from app.api.helpers.permissions import is_user_itself
from app.api.helpers.utilities import get_serializer, str_generator
from app.api.schema.users import UserSchema, UserSchemaPublic
from app.models import db
from app.models.access_code import AccessCode
from app.models.discount_code import DiscountCode
from app.models.email_notification import EmailNotification
from app.models.event_invoice import EventInvoice
from app.models.feedback import Feedback
from app.models.mail import USER_REGISTER_WITH_PASSWORD, PASSWORD_RESET_AND_VERIFY
from app.models.notification import Notification
from app.models.session import Session
from app.models.speaker import Speaker
from app.models.ticket_holder import TicketHolder
from app.models.user import User
from app.models.users_events_role import UsersEventsRoles

user_misc_routes = Blueprint('user_misc', __name__, url_prefix='/v1')


class UserList(ResourceList):
    """
    List and create Users
    """

    def before_create_object(self, data, view_kwargs):
        """
        method to check if there is an existing user with same email which is received in data to create a new user
        and if the password is at least 8 characters long
        :param data:
        :param view_kwargs:
        :return:
        """
        if len(data['password']) < 8:
            raise UnprocessableEntity({'source': '/data/attributes/password'},
                                       'Password should be at least 8 characters long')
        if db.session.query(User.id).filter_by(email=data['email']).scalar() is not None:
            raise ConflictException({'pointer': '/data/attributes/email'}, "Email already exists")

    def after_create_object(self, user, data, view_kwargs):
        """
        method to send-
        email notification
        mail link for register verification
        add image urls
        :param user:
        :param data:
        :param view_kwargs:
        :return:
        """

        if user.was_registered_with_order:
            link = make_frontend_url('/reset-password', {'token': user.reset_password})
            send_email_with_action(user, PASSWORD_RESET_AND_VERIFY, app_name=get_settings()['app_name'],
                                   email=user.email, link=link)
        else:
            s = get_serializer()
            hash = str(base64.b64encode(str(s.dumps([user.email, str_generator()])).encode()), 'utf-8')
            link = make_frontend_url('/verify'.format(id=user.id), {'token': hash})
            send_email_with_action(user, USER_REGISTER_WITH_PASSWORD, app_name=get_settings()['app_name'],
                                   email=user.email)
            send_email_confirmation(user.email, link)
        # TODO Handle in a celery task
        # if data.get('original_image_url'):
        #     try:
        #         uploaded_images = create_save_image_sizes(data['original_image_url'], 'speaker-image', user.id)
        #     except (urllib.error.HTTPError, urllib.error.URLError):
        #         raise UnprocessableEntity(
        #             {'source': 'attributes/original-image-url'}, 'Invalid Image URL'
        #         )
        #     uploaded_images['small_image_url'] = uploaded_images['thumbnail_image_url']
        #     del uploaded_images['large_image_url']
        #     self.session.query(User).filter_by(id=user.id).update(uploaded_images)

        if data.get('avatar_url'):
            start_image_resizing_tasks(user, data['avatar_url'])

    decorators = (api.has_permission('is_admin', methods="GET"),)
    schema = UserSchema
    data_layer = {'session': db.session,
                  'model': User,
                  'methods': {
                      'before_create_object': before_create_object,
                      'after_create_object': after_create_object
                  }}


class UserDetail(ResourceDetail):
    """
    User detail by id
    """

    def before_get(self, args, kwargs):

        if current_user.is_admin or current_user.is_super_admin or current_user:
            self.schema = UserSchema
        else:
            self.schema = UserSchemaPublic

    def before_get_object(self, view_kwargs):
        """
        before get method for user object
        :param view_kwargs:
        :return:
        """
        if view_kwargs.get('notification_id') is not None:
            notification = safe_query(self, Notification, 'id', view_kwargs['notification_id'], 'notification_id')
            if notification.user_id is not None:
                view_kwargs['id'] = notification.user_id
            else:
                view_kwargs['id'] = None

        if view_kwargs.get('feedback_id') is not None:
            feedback = safe_query(self, Feedback, 'id', view_kwargs['feedback_id'], 'feedback_id')
            if feedback.user_id is not None:
                view_kwargs['id'] = feedback.user_id
            else:
                view_kwargs['id'] = None

        if view_kwargs.get('attendee_id') is not None:
            attendee = safe_query(self, TicketHolder, 'id', view_kwargs['attendee_id'], 'attendee_id')
            if attendee.user is not None:
                if (not has_access('is_user_itself',
                                   user_id=attendee.user.id) or not has_access('is_coorganizer',
                                                                               event_id=attendee.event_id)):
                    raise ForbiddenException({'source': ''}, 'Access Forbidden')
                view_kwargs['id'] = attendee.user.id
            else:
                view_kwargs['id'] = None

        if view_kwargs.get('event_invoice_id') is not None:
            event_invoice = safe_query(self, EventInvoice, 'id', view_kwargs['event_invoice_id'], 'event_invoice_id')
            if event_invoice.user_id is not None:
                view_kwargs['id'] = event_invoice.user_id
            else:
                view_kwargs['id'] = None

        if view_kwargs.get('users_events_role_id') is not None:
            users_events_role = safe_query(self, UsersEventsRoles, 'id', view_kwargs['users_events_role_id'],
                                           'users_events_role_id')
            if users_events_role.user_id is not None:
                view_kwargs['id'] = users_events_role.user_id
            else:
                view_kwargs['id'] = None

        if view_kwargs.get('speaker_id') is not None:
            speaker = safe_query(self, Speaker, 'id', view_kwargs['speaker_id'], 'speaker_id')
            if speaker.user_id is not None:
                view_kwargs['id'] = speaker.user_id
            else:
                view_kwargs['id'] = None

        if view_kwargs.get('session_id') is not None:
            session = safe_query(self, Session, 'id', view_kwargs['session_id'], 'session_id')
            if session.creator_id is not None:
                view_kwargs['id'] = session.creator_id
            else:
                view_kwargs['id'] = None

        if view_kwargs.get('access_code_id') is not None:
            access_code = safe_query(self, AccessCode, 'id', view_kwargs['access_code_id'], 'access_code_id')
            if access_code.marketer_id is not None:
                view_kwargs['id'] = access_code.marketer_id
            else:
                view_kwargs['id'] = None

        if view_kwargs.get('discount_code_id') is not None:
            discount_code = safe_query(self, DiscountCode, 'id', view_kwargs['discount_code_id'], 'discount_code_id')
            if discount_code.marketer_id is not None:
                view_kwargs['id'] = discount_code.marketer_id
            else:
                view_kwargs['id'] = None

        if view_kwargs.get('email_notification_id') is not None:
            email_notification = safe_query(self, EmailNotification, 'id', view_kwargs['email_notification_id'],
                                            'email_notification_id')
            if email_notification.user_id is not None:
                view_kwargs['id'] = email_notification.user_id
            else:
                view_kwargs['id'] = None

    def before_update_object(self, user, data, view_kwargs):
        # TODO: Make a celery task for this
        # if data.get('avatar_url') and data['original_image_url'] != user.original_image_url:
        #     try:
        #         uploaded_images = create_save_image_sizes(data['original_image_url'], 'speaker-image', user.id)
        #     except (urllib.error.HTTPError, urllib.error.URLError):
        #         raise UnprocessableEntity(
        #             {'source': 'attributes/original-image-url'}, 'Invalid Image URL'
        #         )
        #     data['original_image_url'] = uploaded_images['original_image_url']
        #     data['small_image_url'] = uploaded_images['thumbnail_image_url']
        #     data['thumbnail_image_url'] = uploaded_images['thumbnail_image_url']
        #     data['icon_image_url'] = uploaded_images['icon_image_url']

        if data.get('email') and data['email'] != user.email:
            try:
                db.session.query(User).filter_by(email=data['email']).one()
            except NoResultFound:
                view_kwargs['email_changed'] = user.email
            else:
                raise ConflictException({'pointer': '/data/attributes/email'}, "Email already exists")

        if has_access('is_super_admin') and data.get('is_admin') and data.get('is_admin') != user.is_admin:
            user.is_admin = not user.is_admin

        if has_access('is_admin') and ('is_sales_admin' in data) and data.get('is_sales_admin') != user.is_sales_admin:
            user.is_sales_admin = not user.is_sales_admin

        if has_access('is_admin') and ('us_marketer' in data) and data.get('is_marketer') != user.is_marketer:
            user.is_marketer = not user.is_marketer

        if data.get('avatar_url'):
            start_image_resizing_tasks(user, data['avatar_url'])

    def after_update_object(self, user, data, view_kwargs):
        """
        method to mail user about email change
        :param user:
        :param data:
        :param view_kwargs:
        :return:
        """
        if view_kwargs.get('email_changed'):
            send_email_change_user_email(user, view_kwargs.get('email_changed'))

    decorators = (api.has_permission('is_user_itself', fetch="user_id,id", fetch_as="user_id",
                                     model=[Notification, Feedback, UsersEventsRoles, Session, EventInvoice, AccessCode,
                                            DiscountCode, EmailNotification, Speaker, User],
                                     fetch_key_url="notification_id, feedback_id, users_events_role_id, session_id, \
                  event_invoice_id, access_code_id, discount_code_id, email_notification_id, speaker_id, id",
                                     leave_if=lambda a: a.get('attendee_id')),)
    schema = UserSchema
    data_layer = {'session': db.session,
                  'model': User,
                  'methods': {
                      'before_get_object': before_get_object,
                      'before_update_object': before_update_object,
                      'after_update_object': after_update_object
                  }}


class UserRelationship(ResourceRelationship):
    """
    User Relationship
    """
    decorators = (is_user_itself,)
    schema = UserSchema
    data_layer = {'session': db.session,
                  'model': User}


@user_misc_routes.route('/users/checkEmail', methods=['POST'])
def is_email_available():
    email = request.json.get('email', None)
    if email:
        if get_count(db.session.query(User).filter_by(email=email)):
            return jsonify(
                result="False"
            )
        else:
            return jsonify(
                result="True"
            )
    else:
        abort(
            make_response(jsonify(error="Email field missing"), 422)
        )


def start_image_resizing_tasks(user, original_image_url):
    user_id = str(user.id)
    from .helpers.tasks import resize_user_images_task
    resize_user_images_task.delay(user_id, original_image_url)
