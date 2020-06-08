import pytest

from app.api.helpers.notification import (
    send_followup_notif_monthly_fee_payment,
    send_notif_after_event,
    send_notif_after_export,
    send_notif_after_import,
    send_notif_event_role,
    send_notif_monthly_fee_payment,
    send_notif_new_session_organizer,
    send_notif_session_accept_reject,
    send_notif_ticket_purchase_organizer,
)
from app.models.notification import Notification
from tests.factories.session import SessionFactory
from tests.factories.user import UserFactory

link = 'https://test.link'


@pytest.fixture
def user(db):
    return UserFactory()


@pytest.fixture
def session(db):
    return SessionFactory()


def test_send_notif_new_session_organizer(user):
    """Method to test new session notification"""
    send_notif_new_session_organizer(user, 'Hobo Meet', link, 1)
    notification = Notification.query.first()
    assert notification.title == 'New session proposal for Hobo Meet'
    assert (
        notification.message
        == 'The event <strong>Hobo Meet</strong> has received a new session proposal.'
    )


def test_send_notif_session_accept_reject(user):
    """Method to test session accept reject notification"""
    send_notif_session_accept_reject(
        user, 'Homeless Therapy', 'accepted', link, 1,
    )
    notification = Notification.query.first()
    assert notification.title == 'Session Homeless Therapy has been accepted'
    assert (
        notification.message
        == 'The session <strong>Homeless Therapy</strong> has been <strong>accepted</strong> '
        'by the Organizer.'
    )


def test_send_notif_after_import(user):
    """Method to test notification after import"""
    send_notif_after_import(
        user, event_name='Tooth Fairy Convention', error_text='TOOTH_NOT_FOUND',
    )
    notification = Notification.query.first()
    assert notification.title == 'Import of event Tooth Fairy Convention failed'
    assert (
        notification.message
        == 'The following error occurred:<br><pre>TOOTH_NOT_FOUND</pre>'
    )


def test_send_notif_after_export(user):
    send_notif_after_export(user, 'Elf Gather', link, 'SLEIGH_BROKEN')
    notification = Notification.query.first()
    assert notification.title == 'Export of event Elf Gather failed'
    assert (
        notification.message
        == 'The following error occurred:<br><pre>SLEIGH_BROKEN</pre>'
    )


def test_send_notif_monthly_fee_payment(user):
    """Method to test monthly fee payment notification"""
    send_notif_monthly_fee_payment(
        user, 'Pizza Party', 'October', 563.65, 'Kite', link, 1
    )
    notification = Notification.query.first()
    assert notification.title == 'October - Monthly service fee invoice for Pizza Party'
    assert (
        notification.message
        == 'The total service fee for the ticket sales of Pizza Party in the '
        'month of October is 563.65.<br/> That payment for the same has to '
        'be made in two weeks.<br><br><em>Thank you for using Kite.</em>'
    )


def test_send_followup_notif_monthly_fee_payment(user):
    send_followup_notif_monthly_fee_payment(
        user, 'Champagne Showers', 'November', 4532.99, 'RedFoo', link, 1,
    )
    notification = Notification.query.first()
    assert (
        notification.title
        == 'Past Due: November - Monthly service fee invoice for Champagne Showers'
    )
    assert (
        notification.message
        == 'The total service fee for the ticket sales of Champagne Showers '
        'in the month of November is 4532.99.<br/> That payment for the '
        'same is past the due date.<br><br><em>Thank you for using '
        'RedFoo.</em>'
    )


def test_send_notif_event_role(user):
    """Method to test event role invite notification"""
    send_notif_event_role(user, 'Dinosaur', 'Mass Extinction', link, 1)
    notification = Notification.query.first()
    assert notification.title == 'Invitation to be Dinosaur at Mass Extinction'
    assert (
        notification.message
        == "You've been invited to be one of the <strong>Dinosaurs</strong> at <strong>Mass Extinction</strong>."
    )


def test_send_notif_after_event(user):
    """Method to test notification after conclusion"""
    send_notif_after_event(user, 'Apocalypse')
    notification = Notification.query.first()
    assert notification.title == 'Event Apocalypse completed'
    assert (
        notification.message
        == 'The event <strong>Apocalypse</strong> has been completed.<br><br>'
    )


def test_send_notif_ticket_purchase_organizer(user):
    """Method to test order invoice notification after purchase"""
    send_notif_ticket_purchase_organizer(user, 's53js79zgd', link, 'Poodle', 1)
    notification = Notification.query.first()
    assert notification.title == 'New ticket purchase for Poodle : (s53js79zgd)'
    assert notification.message == 'The order has been processed successfully.'
