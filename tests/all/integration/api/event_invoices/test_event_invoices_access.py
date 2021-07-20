import json

from app.models.event_invoice import EventInvoice
from tests.factories.event_invoice import EventInvoiceSubFactory
from tests.factories.user import UserFactory


def get_invoice(db, user):
    invoice = EventInvoiceSubFactory(user=user)
    db.session.commit()

    return invoice


def test_invoice_list_user_error(db, client, jwt, user):
    get_invoice(db, user)

    response = client.get(
        '/v1/event-invoices',
        content_type='application/vnd.api+json',
        headers=jwt,
    )

    assert response.status_code == 403


def test_invoice_list_admin(db, client, admin_jwt, user):
    invoice = get_invoice(db, user)
    get_invoice(db, UserFactory())

    response = client.get(
        '/v1/event-invoices',
        content_type='application/vnd.api+json',
        headers=admin_jwt,
    )

    assert response.status_code == 200
    response_dict = json.loads(response.data)
    assert len(response_dict['data']) == 2
    assert response_dict['data'][0]['id'] == str(invoice.id)


def test_invoice_list_user_itself(db, client, jwt, user):
    invoice = get_invoice(db, user)
    other_invoice = get_invoice(db, UserFactory())

    response = client.get(
        f'/v1/users/{user.id}/event-invoices',
        content_type='application/vnd.api+json',
        headers=jwt,
    )

    assert response.status_code == 200
    response_dict = json.loads(response.data)
    assert len(response_dict['data']) == 1
    assert response_dict['data'][0]['id'] == str(invoice.id)
    assert response_dict['data'][0]['id'] != str(other_invoice.id)


def test_invoice_other_user_error(db, client, jwt):
    invoice = get_invoice(db, UserFactory())

    response = client.get(
        f'/v1/event-invoices/{invoice.id}',
        content_type='application/vnd.api+json',
        headers=jwt,
    )

    assert response.status_code == 403


def test_invoice_identifier_other_user_error(db, client, jwt):
    invoice = get_invoice(db, UserFactory())

    response = client.get(
        f'/v1/event-invoices/{invoice.identifier}',
        content_type='application/vnd.api+json',
        headers=jwt,
    )

    assert response.status_code == 403


def test_invoice_admin(db, client, admin_jwt):
    invoice = get_invoice(db, UserFactory())

    response = client.get(
        f'/v1/event-invoices/{invoice.id}',
        content_type='application/vnd.api+json',
        headers=admin_jwt,
    )

    assert response.status_code == 200
    response_dict = json.loads(response.data)
    assert response_dict['data']['id'] == str(invoice.id)


def test_invoice_identifier_admin(db, client, admin_jwt):
    invoice = get_invoice(db, UserFactory())

    response = client.get(
        f'/v1/event-invoices/{invoice.identifier}',
        content_type='application/vnd.api+json',
        headers=admin_jwt,
    )

    assert response.status_code == 200
    response_dict = json.loads(response.data)
    assert response_dict['data']['attributes']['identifier'] == invoice.identifier


def test_invoice_user_itself(db, client, jwt, user):
    invoice = get_invoice(db, user)
    other_invoice = get_invoice(db, UserFactory())

    response = client.get(
        f'/v1/event-invoices/{invoice.id}',
        content_type='application/vnd.api+json',
        headers=jwt,
    )

    assert response.status_code == 200
    response_dict = json.loads(response.data)
    assert response_dict['data']['id'] == str(invoice.id)
    assert response_dict['data']['id'] != str(other_invoice.id)


def test_invoice_identifier_user_itself(db, client, jwt, user):
    invoice = get_invoice(db, user)
    other_invoice = get_invoice(db, UserFactory())

    response = client.get(
        f'/v1/event-invoices/{invoice.identifier}',
        content_type='application/vnd.api+json',
        headers=jwt,
    )

    assert response.status_code == 200
    response_dict = json.loads(response.data)
    assert response_dict['data']['attributes']['identifier'] == invoice.identifier
    assert response_dict['data']['attributes']['identifier'] != other_invoice.identifier


def test_invoice_patch_admin_error(db, client, admin_jwt, user):
    invoice = get_invoice(db, user)
    data = json.dumps(
        {
            'data': {
                'type': 'event-invoice',
                'id': str(invoice.id),
                'attributes': {'amount': 100},
            }
        }
    )

    response = client.patch(
        f'/v1/event-invoices/{invoice.id}',
        content_type='application/vnd.api+json',
        headers=admin_jwt,
        data=data,
    )

    assert response.status_code == 200


def test_invoice_patch_user_error(db, client, jwt, user):
    invoice = get_invoice(db, user)
    data = json.dumps(
        {
            'data': {
                'type': 'event-invoice',
                'id': str(invoice.id),
                'attributes': {'amount': 0},
            }
        }
    )

    response = client.patch(
        f'/v1/event-invoices/{invoice.id}',
        content_type='application/vnd.api+json',
        headers=jwt,
        data=data,
    )

    assert response.status_code == 200


def test_invoice_delete_admin_error(db, client, admin_jwt, user):
    invoice = get_invoice(db, user)

    response = client.delete(
        f'/v1/event-invoices/{invoice.id}',
        content_type='application/vnd.api+json',
        headers=admin_jwt,
    )

    assert response.status_code == 405


def test_invoice_delete_user_error(db, client, jwt, user):
    invoice = get_invoice(db, user)

    response = client.delete(
        f'/v1/event-invoices/{invoice.id}',
        content_type='application/vnd.api+json',
        headers=jwt,
    )

    assert response.status_code == 405


def test_invoice_post_admin_error(client, admin_jwt):
    data = json.dumps(
        {
            'data': {
                'type': 'event-invoice',
                'attributes': {'amount': 100},
            }
        }
    )

    response = client.post(
        '/v1/event-invoices',
        content_type='application/vnd.api+json',
        headers=admin_jwt,
        data=data,
    )

    assert response.status_code == 405
    assert EventInvoice.query.count() == 0


def test_invoice_post_user_error(client, jwt):
    data = json.dumps(
        {
            'data': {
                'type': 'event-invoice',
                'attributes': {'amount': 100},
            }
        }
    )

    response = client.post(
        '/v1/event-invoices',
        content_type='application/vnd.api+json',
        headers=jwt,
        data=data,
    )

    assert response.status_code == 405
    assert EventInvoice.query.count() == 0
