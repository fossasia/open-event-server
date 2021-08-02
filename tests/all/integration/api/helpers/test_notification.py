import pytest

from app.api.helpers.db import get_or_create
from app.api.helpers.notification import (
    notify_event_role_invitation,
    notify_monthly_payment,
    notify_new_session,
    notify_session_state_change,
    notify_ticket_purchase_attendee,
)
from app.models.notification import Notification, NotificationType
from app.models.role import Role
from app.models.users_events_role import UsersEventsRoles
from tests.factories.attendee import AttendeeOrderSubFactory
from tests.factories.event_invoice import EventInvoiceSubFactory
from tests.factories.order import OrderSubFactory
from tests.factories.role_invite import RoleInviteSubFactory
from tests.factories.session import SessionSubFactory
from tests.factories.speaker import SpeakerSubFactory
from tests.factories.user import UserFactory

link = 'https://test.link'


@pytest.fixture
def session(db):
    session = SessionSubFactory()
    session.creator = UserFactory()
    create_owner(db, session.event)

    return session


def create_owner(db, event):
    role, _ = get_or_create(Role, name='owner', title_name='Owner')
    UsersEventsRoles(user=UserFactory(), event=event, role=role)
    db.session.commit()


def test_notify_new_session_organizer(session):
    notify_new_session(session)

    notification = Notification.query.first()
    assert notification.user_id == session.event.owner.id
    assert notification.content.type == NotificationType.NEW_SESSION
    assert notification.content.target == session
    assert notification.content.actors[0].actor == session.creator


def test_notify_session_state_change(db, session):
    session.state == 'accepted'
    session.speakers = [SpeakerSubFactory(email='test@example.org')]
    user = UserFactory(_email='test@example.org')
    db.session.commit()

    notify_session_state_change(session, session.event.owner)

    notification = Notification.query.first()
    assert notification.user == user
    assert notification.content.type == NotificationType.SESSION_STATE_CHANGE
    assert notification.content.target == session
    assert notification.content.target_action == 'accepted'
    assert notification.content.actors[0].actor == session.event.owner


def test_notify_monthly_fee_payment(db):
    invoice = EventInvoiceSubFactory(user=UserFactory())
    db.session.commit()
    notify_monthly_payment(invoice)

    notification = Notification.query.first()
    assert notification.user == invoice.user
    assert notification.content.type == NotificationType.MONTHLY_PAYMENT
    assert notification.content.target == invoice
    assert notification.content.actors == []


def test_notify_monthly_fee_payment_follow_up(db):
    invoice = EventInvoiceSubFactory(user=UserFactory())
    db.session.commit()
    notify_monthly_payment(invoice, follow_up=True)

    notification = Notification.query.first()
    assert notification.user == invoice.user
    assert notification.content.type == NotificationType.MONTHLY_PAYMENT_FOLLOWUP
    assert notification.content.target == invoice
    assert notification.content.actors == []


def test_notify_event_role(db):
    invite = RoleInviteSubFactory()
    role, _ = get_or_create(Role, name='owner', title_name='Owner')
    UsersEventsRoles(user=UserFactory(), event=invite.event, role=role)
    user = UserFactory()
    db.session.commit()
    notify_event_role_invitation(invite, user, invite.event.owner)

    notification = Notification.query.first()
    assert notification.user == user
    assert notification.content.type == NotificationType.EVENT_ROLE
    assert notification.content.target == invite
    assert notification.content.actors[0].actor == invite.event.owner


def test_notify_ticket_purchase_atttendee(db):
    order = OrderSubFactory(user=UserFactory())
    attendee = AttendeeOrderSubFactory(order=order, email='test@example.org')
    UserFactory(_email='test@example.org')
    db.session.commit()

    notify_ticket_purchase_attendee(order)
    notifications = Notification.query.order_by(Notification.id).all()

    notification_buyer = notifications[0]
    assert notification_buyer.user == order.user
    assert notification_buyer.content.type == NotificationType.TICKET_PURCHASED
    assert notification_buyer.content.target == order
    assert notification_buyer.content.actors[0].actor == order.user

    notification = notifications[1]
    assert notification.user == attendee.user
    assert notification.content.type == NotificationType.TICKET_PURCHASED_ATTENDEE
    assert notification.content.target == order
    assert notification.content.actors[0].actor == order.user
