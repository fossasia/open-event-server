import json

from app.models.custom_form import CustomForms
from tests.factories.event import EventFactoryBasic


def test_custom_form_create(db, client, user, jwt):
    user.is_super_admin = True
    event = EventFactoryBasic(owner=user)
    db.session.commit()

    data = json.dumps(
        {
            'data': {
                'type': 'custom-form',
                "attributes": {
                    "form": "attendee",
                    "type": "email",
                    "field-identifier": "email",
                    "is-included": True,
                    "is-required": True,
                    "is-complex": False,
                    "form-id": "60af0a01-ca58-4121-a559-edc21c3dd233",
                    "main-language": "en-US",
                    "translations": [{"name": "email-ES", "language_code": "es-ES"}],
                },
                "relationships": {
                    "event": {"data": {"id": str(event.id), "type": "event"}}
                },
            }
        }
    )

    response = client.post(
        '/v1/custom-forms',
        content_type='application/vnd.api+json',
        headers=jwt,
        data=data,
    )

    assert response.status_code == 201
    c_id = json.loads(response.data)['data']['id']
    custom_form = CustomForms.query.get(c_id)

    assert custom_form.form == 'attendee'
    assert custom_form.type == 'email'
    assert custom_form.name == 'Email'
    assert custom_form.field_identifier == 'email'
    assert custom_form.is_complex is False

    data = json.dumps(
        {
            'data': {
                'type': 'custom-form',
                "attributes": {
                    "form": "attendee",
                    "type": "number",
                    "field-identifier": "vortexTensor",
                    "name": "Vortex Tensor",
                    "is-included": True,
                    "is-required": True,
                    "is-complex": True,
                },
                "relationships": {
                    "event": {"data": {"id": str(event.id), "type": "event"}}
                },
            }
        }
    )

    response = client.post(
        '/v1/custom-forms',
        content_type='application/vnd.api+json',
        headers=jwt,
        data=data,
    )

    assert response.status_code == 201
    c_id = json.loads(response.data)['data']['id']
    custom_form = CustomForms.query.get(c_id)

    assert custom_form.form == 'attendee'
    assert custom_form.type == 'number'
    assert custom_form.identifier == 'vortex_tensor'
    assert custom_form.is_complex is True
