import json

from app.models.badge_field_form import BadgeFieldForms
from tests.factories import common
from tests.factories.badge_field_form import BadgeFieldFormFactory
from tests.factories.badge_form import BadgeFormFactory
from tests.factories.event import EventFactoryBasic
from tests.factories.ticket import TicketFactory


def test_get_badge_form_by_ticket(db, client, jwt):
    """Test get badge form by ticket."""
    event = EventFactoryBasic()
    ticket = TicketFactory(
        event=event,
        badge_id=common.string_,
    )
    badge_form = BadgeFormFactory(
        event=event,
        badge_id=ticket.badge_id,
    )
    BadgeFieldFormFactory(
        badge_form=badge_form,
        badge_id=ticket.badge_id,
    )
    db.session.commit()

    response = client.get(
        f'v1/tickets/{ticket.id}/badge-forms',
        content_type='application/vnd.api+json',
        headers=jwt,
    )

    assert response.status_code == 200

    count = BadgeFieldForms.query.filter_by(badge_id=ticket.badge_id).count()
    assert len(json.loads(response.data)) == count
