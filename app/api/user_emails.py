from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship

from app.api.bootstrap import api
from app.api.helpers.db import get_count, safe_query_kwargs
from app.api.helpers.errors import ConflictError
from app.api.helpers.utilities import require_relationship
from app.api.schema.user_email import UserEmailSchema
from app.models import db
from app.models.user import User
from app.models.user_email import UserEmail


class UserEmailListAdmin(ResourceList):
    """
    Admin List for User Emails
    """

    methods = [
        'GET',
    ]
    schema = UserEmailSchema
    decorators = (api.has_permission('is_admin'),)
    data_layer = {'session': db.session, 'model': UserEmail}


class UserEmailList(ResourceList):
    """
    List User Emails for a user
    """

    def query(self, view_kwargs):
        """
        query method for Notifications list
        :param view_kwargs:
        :return:
        """
        query_ = self.session.query(UserEmail)
        if view_kwargs.get('user_id'):
            user = safe_query_kwargs(User, view_kwargs, 'user_id')
            query_ = query_.join(User).filter(User.id == user.id)
        return query_

    view_kwargs = True
    decorators = (
        api.has_permission(
            'is_user_itself', fetch="user_id", model=UserEmail, methods="GET"
        ),
    )
    methods = [
        "GET",
    ]
    schema = UserEmailSchema
    data_layer = {'session': db.session, 'model': UserEmail, 'methods': {'query': query}}


class UserEmailListPost(ResourceList):
    """
    Create new alternate email for a user
    """

    def before_post(self, args, kwargs, data):
        """
        before post method to check for required relationship and proper permission
        :param args:
        :param kwargs:
        :param data:
        :return:
        """
        require_relationship(['user'], data)

        if (
            get_count(
                db.session.query(UserEmail.id).filter_by(
                    email_address=data.get('email-address'),
                    user_id=int(data['user']),
                    deleted_at=None,
                )
            )
            > 0
        ):
            raise ConflictError(
                {'pointer': '/data/attributes/name'}, "Email already exists"
            )

    schema = UserEmailSchema
    methods = [
        'POST',
    ]
    data_layer = {'session': db.session, 'model': UserEmail}


class UserEmailDetail(ResourceDetail):
    """
    User Email detail by id
    """

    schema = UserEmailSchema
    decorators = (
        api.has_permission(
            'is_user_itself',
            fetch='user_id',
            model=UserEmail,
            methods="PATCH,DELETE",
        ),
    )
    data_layer = {'session': db.session, 'model': UserEmail}


class UserEmailRelationship(ResourceRelationship):
    """
    User Email Relationship
    """

    decorators = (
        api.has_permission(
            'is_user_itself', fetch='user_id', model=UserEmail, methods="GET"
        ),
    )
    schema = UserEmailSchema
    data_layer = {'session': db.session, 'model': UserEmail}
