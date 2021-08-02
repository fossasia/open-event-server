import logging
from typing import Union

from flask import request
from flask_jwt_extended import current_user, verify_jwt_in_request
from sqlalchemy.orm.exc import NoResultFound

from app.api.helpers.errors import ForbiddenError, NotFoundError
from app.api.helpers.jwt import get_identity
from app.api.helpers.permissions import jwt_required
from app.models.event import Event
from app.models.event_invoice import EventInvoice
from app.models.order import Order
from app.models.session import Session
from app.models.speaker import Speaker
from app.models.user import User

logger = logging.getLogger(__name__)


@jwt_required
def auth_required(view, view_args, view_kwargs, *args, **kwargs):
    return view(*view_args, **view_kwargs)


@jwt_required
def is_super_admin(view, view_args, view_kwargs, *args, **kwargs):
    """
    Permission function for things allowed exclusively to super admin.
    Do not use this if the resource is also accessible by a normal admin,
    use the is_admin decorator instead.
    :return:
    """
    user = current_user
    if not user.is_super_admin:
        raise ForbiddenError({'source': ''}, 'Super admin access is required')
    return view(*view_args, **view_kwargs)


@jwt_required
def is_admin(view, view_args, view_kwargs, *args, **kwargs):
    user = current_user
    if not user.is_admin and not user.is_super_admin:
        raise ForbiddenError({'source': ''}, 'Admin access is required')

    return view(*view_args, **view_kwargs)


@jwt_required
def is_owner(view, view_args, view_kwargs, *args, **kwargs):
    user = current_user

    if user.is_staff:
        return view(*view_args, **view_kwargs)

    if not user.is_owner(kwargs['event_id']):
        raise ForbiddenError({'source': ''}, 'Owner access is required')

    return view(*view_args, **view_kwargs)


@jwt_required
def is_organizer(view, view_args, view_kwargs, *args, **kwargs):
    user = current_user

    if user.is_staff:
        return view(*view_args, **view_kwargs)

    event_id = kwargs.get('event_id')
    if event_id and (user.is_owner(event_id) or user.is_organizer(event_id)):
        return view(*view_args, **view_kwargs)

    raise ForbiddenError({'source': ''}, 'Organizer access is required')


@jwt_required
def is_coorganizer(view, view_args, view_kwargs, *args, **kwargs):
    user = current_user

    if user.is_staff:
        return view(*view_args, **view_kwargs)

    if user.has_event_access(kwargs['event_id']):
        return view(*view_args, **view_kwargs)

    raise ForbiddenError({'source': ''}, 'Co-organizer access is required.')


@jwt_required
def is_coorganizer_but_not_admin(view, view_args, view_kwargs, *args, **kwargs):
    user = current_user

    if user.has_event_access(kwargs['event_id']):
        return view(*view_args, **view_kwargs)

    raise ForbiddenError({'source': ''}, 'Co-organizer access is required.')


def is_coorganizer_endpoint_related_to_event(
    view, view_args, view_kwargs, *args, **kwargs
):
    """
     If the authorization header is present (but expired)
     and the eventbeing accessed is not published
     - And the user is related to the event (organizer, co-organizer etc) show a 401
     - Else show a 404

    :param view:
    :param view_args:
    :param view_kwargs:
    :param args:
    :param kwargs:
    :return:
    """
    user = get_identity()

    if user:
        if user.is_staff:
            verify_jwt_in_request()
            return view(*view_args, **view_kwargs)

        if user.has_event_access(kwargs['event_id']):
            verify_jwt_in_request()
            return view(*view_args, **view_kwargs)

    raise ForbiddenError({'source': ''}, 'Co-organizer access is required.')


@jwt_required
def is_user_itself(view, view_args, view_kwargs, *args, **kwargs):
    """
    Allows admin and super admin access to any resource irrespective of id.
    Otherwise the user can only access his/her resource.
    """
    user = current_user
    if not user.is_admin and not user.is_super_admin and user.id != kwargs['user_id']:
        raise ForbiddenError({'source': ''}, 'Access Forbidden')
    return view(*view_args, **view_kwargs)


@jwt_required
def is_coorganizer_or_user_itself(view, view_args, view_kwargs, *args, **kwargs):
    """
    Allows admin and super admin access to any resource irrespective of id.
    Otherwise the user can only access his/her resource.
    """
    user = current_user

    if (
        user.is_admin
        or user.is_super_admin
        or ('user_id' in kwargs and user.id == kwargs['user_id'])
    ):
        return view(*view_args, **view_kwargs)

    if user.is_staff:
        return view(*view_args, **view_kwargs)

    if user.has_event_access(kwargs['event_id']):
        return view(*view_args, **view_kwargs)

    raise ForbiddenError({'source': ''}, 'Co-organizer access is required.')


@jwt_required
def is_speaker_for_session(view, view_args, view_kwargs, *args, **kwargs):
    """
    Allows admin and super admin access to any resource irrespective of id.
    Otherwise the user can only access his/her resource.
    """
    not_found = NotFoundError({'parameter': 'id'}, 'Session not found.')
    try:
        session = Session.query.filter(Session.id == view_kwargs['id']).one()
    except NoResultFound:
        raise not_found

    user = current_user

    if user.is_staff:
        return view(*view_args, **view_kwargs)

    if session.deleted_at is not None:
        raise not_found

    if user.has_event_access(session.event_id):
        return view(*view_args, **view_kwargs)

    if session.speakers:
        for speaker in session.speakers:
            if speaker.user_id == user.id or speaker.email == user._email:
                return view(*view_args, **view_kwargs)

    if session.creator_id == user.id:
        return view(*view_args, **view_kwargs)

    raise ForbiddenError({'source': ''}, 'Access denied.')


@jwt_required
def is_speaker_itself_or_admin(view, view_args, view_kwargs, *args, **kwargs):
    """
    Allows admin and super admin access to any resource irrespective of id.
    Otherwise the user can only access his/her resource.
    """
    user = current_user

    if user.is_admin or user.is_super_admin:
        return view(*view_args, **view_kwargs)

    if user.has_event_access(kwargs['event_id']):
        return view(*view_args, **view_kwargs)

    if ('model' in kwargs) and (kwargs['model'] == Speaker):
        query_user = Speaker.query.filter_by(email=user._email).first()
        if query_user:
            return view(*view_args, **view_kwargs)

    raise ForbiddenError({'source': ''}, 'Detail ownership is required, access denied.')


@jwt_required
def is_session_self_submitted(view, view_args, view_kwargs, *args, **kwargs):
    """
    Allows admin and super admin access to any resource irrespective of id.
    Otherwise the user can only access his/her resource.
    """
    user = current_user
    if user.is_admin or user.is_super_admin:
        return view(*view_args, **view_kwargs)

    if user.is_staff:
        return view(*view_args, **view_kwargs)

    try:
        session = Session.query.filter(Session.id == kwargs['session_id']).one()
    except NoResultFound:
        raise NotFoundError({'parameter': 'session_id'}, 'Session not found.')

    if user.has_event_access(session.event_id):
        return view(*view_args, **view_kwargs)

    if session.creator_id == user.id:
        return view(*view_args, **view_kwargs)

    raise ForbiddenError({'source': ''}, 'Access denied.')


@jwt_required
def is_registrar(view, view_args, view_kwargs, *args, **kwargs):
    """
    Allows Organizer, Co-organizer and registrar to access the event resources.x`
    """
    user = current_user
    event_id = kwargs['event_id']

    if user.is_staff:
        return view(*view_args, **view_kwargs)
    if user.is_registrar(event_id) or user.has_event_access(event_id):
        return view(*view_args, **view_kwargs)
    raise ForbiddenError({'source': ''}, 'Registrar Access is Required.')


@jwt_required
def is_registrar_or_user_itself(view, view_args, view_kwargs, *args, **kwargs):
    """
    Allows admin and super admin access to any resource irrespective of id.
    Otherwise the user can only access his/her resource.
    """
    user = current_user
    if user.is_admin or user.is_super_admin or user.id == kwargs['user_id']:
        return view(*view_args, **view_kwargs)

    if user.is_staff:
        return view(*view_args, **view_kwargs)

    event_id = kwargs['event_id']
    if user.is_registrar(event_id) or user.has_event_access(event_id):
        return view(*view_args, **view_kwargs)

    raise ForbiddenError({'source': ''}, 'Registrar access is required.')


@jwt_required
def is_track_organizer(view, view_args, view_kwargs, *args, **kwargs):
    """
    Allows Organizer, Co-organizer and Track Organizer to access the resource(s).
    """
    user = current_user
    event_id = kwargs['event_id']

    if user.is_staff:
        return view(*view_args, **view_kwargs)
    if user.is_track_organizer(event_id) or user.has_event_access(event_id):
        return view(*view_args, **view_kwargs)
    raise ForbiddenError({'source': ''}, 'Track Organizer access is Required.')


@jwt_required
def is_moderator(view, view_args, view_kwargs, *args, **kwargs):
    """
    Allows Organizer, Co-organizer and Moderator to access the resource(s).
    """
    user = current_user
    event_id = kwargs['event_id']
    if user.is_staff:
        return view(*view_args, **view_kwargs)
    if user.is_moderator(event_id) or user.has_event_access(event_id):
        return view_kwargs(*view_args, **view_kwargs)
    raise ForbiddenError({'source': ''}, 'Moderator Access is Required.')


@jwt_required
def user_event(view, view_args, view_kwargs, *args, **kwargs):
    user = current_user
    view_kwargs['user_id'] = user.id
    return view(*view_args, **view_kwargs)


def accessible_role_based_events(view, view_args, view_kwargs, *args, **kwargs):
    if 'POST' in request.method or 'withRole' in request.args:
        verify_jwt_in_request()
        user = current_user

        if 'GET' in request.method and user.is_staff:
            return view(*view_args, **view_kwargs)
        view_kwargs['user_id'] = user.id

    return view(*view_args, **view_kwargs)


def create_event(view, view_args, view_kwargs, *args, **kwargs):
    if 'POST' in request.method or 'withRole' in request.args:
        verify_jwt_in_request()
        user = current_user

        if user.can_create_event is False:
            raise ForbiddenError({'source': ''}, 'Please verify your email')

        if 'GET' in request.method and user.is_staff:
            return view(*view_args, **view_kwargs)
        view_kwargs['user_id'] = user.id

    return view(*view_args, **view_kwargs)


permissions = {
    'is_super_admin': is_super_admin,
    'is_admin': is_admin,
    'is_owner': is_owner,
    'is_organizer': is_organizer,
    'is_coorganizer': is_coorganizer,
    'is_track_organizer': is_track_organizer,
    'is_registrar': is_registrar,
    'is_moderator': is_moderator,
    'user_event': user_event,
    'accessible_role_based_events': accessible_role_based_events,
    'auth_required': auth_required,
    'is_speaker_for_session': is_speaker_for_session,
    'is_session_self_submitted': is_session_self_submitted,
    'is_coorganizer_or_user_itself': is_coorganizer_or_user_itself,
    'create_event': create_event,
    'is_user_itself': is_user_itself,
    'is_coorganizer_endpoint_related_to_event': is_coorganizer_endpoint_related_to_event,
    'is_registrar_or_user_itself': is_registrar_or_user_itself,
    'is_coorganizer_but_not_admin': is_coorganizer_but_not_admin,
    'is_speaker_itself_or_admin': is_speaker_itself_or_admin,
}


def is_multiple(data: Union[str, list]) -> bool:
    if type(data) is list:
        return True
    if type(data) is str:
        if data.find(",") > 0:
            return True
    return False


def permission_manager(view, view_args, view_kwargs, *args, **kwargs):
    """The function use to check permissions

    :param callable view: the view
    :param list view_args: view args
    :param dict view_kwargs: view kwargs
    :param list args: decorator args
    :param dict kwargs: decorator kwargs
    """
    methods = 'GET,POST,DELETE,PATCH'

    if 'id' in kwargs:
        view_kwargs['id'] = kwargs['id']

    if kwargs.get('methods'):
        methods = kwargs['methods']

    if request.method not in methods:
        return view(*view_args, **view_kwargs)

    # leave_if checks if we have to bypass this request on the basis of lambda function
    if 'leave_if' in kwargs:
        check = kwargs['leave_if']
        if check(view_kwargs):
            return view(*view_args, **view_kwargs)

    # A check to ensure it is good to go ahead and check permissions
    if 'check' in kwargs:
        check = kwargs['check']
        if not check(view_kwargs):
            raise ForbiddenError({'source': ''}, 'Access forbidden')

    # For Orders API
    if 'order_identifier' in view_kwargs:
        try:
            order = Order.query.filter_by(
                identifier=view_kwargs['order_identifier']
            ).one()
        except NoResultFound:
            raise NotFoundError({'parameter': 'order_identifier'}, 'Order not found')
        view_kwargs['id'] = order.id

    # If event_identifier in route instead of event_id
    if 'event_identifier' in view_kwargs:
        try:
            event = Event.query.filter_by(
                identifier=view_kwargs['event_identifier']
            ).one()
        except NoResultFound:
            raise NotFoundError({'parameter': 'event_identifier'}, 'Event not found')
        view_kwargs['event_id'] = event.id

    if view_kwargs.get('event_invoice_identifier') is not None:
        try:
            event_invoice = EventInvoice.query.filter_by(
                identifier=view_kwargs['event_invoice_identifier']
            ).one()
        except NoResultFound:
            NotFoundError(
                {'parameter': 'event_invoice_identifier'}, 'Event Invoice not found'
            )
        view_kwargs['id'] = event_invoice.id

    # Only for events API
    if 'identifier' in view_kwargs:
        try:
            event = Event.query.filter_by(identifier=view_kwargs['identifier']).one()
        except NoResultFound:
            raise NotFoundError({'parameter': 'identifier'}, 'Event not found')
        view_kwargs['id'] = event.id

    if 'fetch' in kwargs:
        fetched = None
        if is_multiple(kwargs['fetch']):
            kwargs['fetch'] = [f.strip() for f in kwargs['fetch'].split(",")]
            for f in kwargs['fetch']:
                if f in view_kwargs:
                    fetched = view_kwargs.get(f)
                    break
        elif kwargs['fetch'] in view_kwargs:
            fetched = view_kwargs[kwargs['fetch']]
        if not fetched:
            model = kwargs['model']
            fetch = kwargs['fetch']
            fetch_key_url = 'id'
            fetch_key_model = 'id'
            if kwargs.get('fetch_key_url'):
                fetch_key_url = kwargs['fetch_key_url']

            if kwargs.get('fetch_key_model'):
                fetch_key_model = kwargs['fetch_key_model']

            if not is_multiple(model):
                model = [model]

            if isinstance(fetch_key_url, str) and is_multiple(fetch_key_url):
                fetch_key_url = fetch_key_url.split(  # pytype: disable=attribute-error
                    ","
                )

            found = False
            for index, mod in enumerate(model):
                if is_multiple(fetch_key_url):
                    f_url = fetch_key_url[index].strip()
                else:
                    f_url = fetch_key_url
                if not view_kwargs.get(f_url):
                    continue
                try:
                    data = mod.query.filter(  # pytype: disable=attribute-error
                        getattr(mod, fetch_key_model) == view_kwargs[f_url]
                    ).one()
                except NoResultFound:
                    pass
                else:
                    found = True
                    break

            if not found:
                raise NotFoundError({'source': ''}, 'Object not found.')

            fetched = None
            if is_multiple(fetch):
                for f in fetch:
                    if hasattr(data, f):
                        fetched = getattr(data, f)
                        break
            else:
                fetched = getattr(data, fetch) if hasattr(data, fetch) else None

        if fetched:
            fetch_as = kwargs.get('fetch_as')
            fetch = kwargs.get('fetch')
            if fetch_as == fetch:
                logger.warning(
                    "If 'fetch_as' is same as 'fetch', then it is redundant: %s", fetch
                )
            if fetch_as:
                kwargs[fetch_as] = fetched
            elif fetch:
                kwargs[fetch] = fetched
        else:
            raise NotFoundError({'source': ''}, 'Object not found.')
    if args[0] in permissions:
        return permissions[args[0]](view, view_args, view_kwargs, *args, **kwargs)
    raise ForbiddenError({'source': ''}, 'Access forbidden')


def has_access(access_level, **kwargs):
    """
    The method to check if the logged in user has specified access
    level or nor
    :param string access_level: name of access level
    :param dict kwargs: This is directly passed to permission manager
    :return: bool: True if passes the access else False
    """
    if access_level in permissions:
        try:
            auth = permissions[access_level](
                lambda *a, **b: True, (), kwargs, (), **kwargs
            )
            if type(auth) is bool and auth is True:
                return True
        except ForbiddenError:
            pass
    return False


def is_logged_in() -> bool:
    return 'Authorization' in request.headers


def require_current_user() -> Union[User, None]:
    """Parses JWT and returns current_user if Authorization header is present, else None"""
    if not is_logged_in():
        return None
    verify_jwt_in_request()
    return current_user
