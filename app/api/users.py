import base64

from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship

from app import get_settings
from app.api.bootstrap import api
from app.api.helpers.files import create_save_image_sizes, make_frontend_url
from app.api.helpers.mail import send_email_confirmation, send_email_change_user_email, send_email_with_action
from app.api.helpers.permissions import is_user_itself
from app.api.helpers.utilities import get_serializer, str_generator
from app.api.schema.users import UserSchema
from app.models import db
from app.models.access_code import AccessCode
from app.models.discount_code import DiscountCode
from app.models.email_notification import EmailNotification
from app.models.event_invoice import EventInvoice
from app.models.mail import USER_REGISTER_WITH_PASSWORD
from app.models.notification import Notification
from app.models.feedback import Feedback
from app.models.speaker import Speaker
from app.models.session import Session
from app.api.helpers.exceptions import ConflictException
from app.api.helpers.db import safe_query
from app.models.user import User
from app.models.users_events_role import UsersEventsRoles
from app.models.ticket_holder import TicketHolder
from app.api.helpers.exceptions import ForbiddenException
from app.api.helpers.permission_manager import has_access


class UserList(ResourceList):
    """
    List and create Users
    """
    def before_create_object(self, data, view_kwargs):
        """
        method to check if there is an existing user with same email which is recieved in data to create a new user
        :param data:
        :param view_kwargs:
        :return:
        """
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
        s = get_serializer()
        hash = str(base64.b64encode(str(s.dumps([user.email, str_generator()])).encode()), 'utf-8')
        link = make_frontend_url('/email/verify'.format(id=user.id), {'token': hash})
        send_email_with_action(user, USER_REGISTER_WITH_PASSWORD, app_name=get_settings()['app_name'],
                               email=user.email)
        send_email_confirmation(user.email, link)

        if data.get('original_image_url'):
            uploaded_images = create_save_image_sizes(data['original_image_url'], 'user', user.id)
            uploaded_images['small_image_url'] = uploaded_images['thumbnail_image_url']
            del uploaded_images['large_image_url']
            self.session.query(User).filter_by(id=user.id).update(uploaded_images)

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
            print(view_kwargs['feedback_id'])
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
        if data.get('original_image_url') and data['original_image_url'] != user.original_image_url:
            uploaded_images = create_save_image_sizes(data['original_image_url'], 'user', user.id)
            data['original_image_url'] = uploaded_images['original_image_url']
            data['small_image_url'] = uploaded_images['thumbnail_image_url']
            data['thumbnail_image_url'] = uploaded_images['thumbnail_image_url']
            data['icon_image_url'] = uploaded_images['icon_image_url']

        if data.get('email') and data['email'] != user.email:
            view_kwargs['email_changed'] = user.email

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
                                     leave_if=lambda a: a.get('attendee_id')), )
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
    decorators = (is_user_itself, )
    schema = UserSchema
    data_layer = {'session': db.session,
                  'model': User}
