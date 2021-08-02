import json

from tests.factories.order import OrderSubFactory


def test_nested_sorting(db, client, admin_jwt):
    OrderSubFactory(event__name='Shah', identifier='zxcv')
    OrderSubFactory(event__name='Abu', identifier='abcde')
    OrderSubFactory(event__name='Xerxes', identifier='fghj')

    db.session.commit()

    response = client.get(
        '/v1/orders?sort=event.name',
        content_type='application/vnd.api+json',
        headers=admin_jwt,
    )

    orders = json.loads(response.data)['data']
    assert orders[0]['attributes']['identifier'] == 'abcde'
    assert orders[1]['attributes']['identifier'] == 'zxcv'
    assert orders[2]['attributes']['identifier'] == 'fghj'

    response = client.get(
        '/v1/orders?sort=-event.name',
        content_type='application/vnd.api+json',
        headers=admin_jwt,
    )

    orders = json.loads(response.data)['data']
    assert orders[0]['attributes']['identifier'] == 'fghj'
    assert orders[1]['attributes']['identifier'] == 'zxcv'
    assert orders[2]['attributes']['identifier'] == 'abcde'

    response = client.get(
        '/v1/orders?sort=identifier',
        content_type='application/vnd.api+json',
        headers=admin_jwt,
    )

    orders = json.loads(response.data)['data']
    assert orders[0]['attributes']['identifier'] == 'abcde'
    assert orders[1]['attributes']['identifier'] == 'fghj'
    assert orders[2]['attributes']['identifier'] == 'zxcv'
