import json


def test_payment_gateway(db, client):
    response = client.get('/v1/settings')
    assert response.status_code == 200
    data = json.loads(response.data)["data"]["attributes"]
    assert "stripe-client-id" in data
    assert "stripe-publishable-key" in data
    assert "stripe-test-client-id" in data
    assert "stripe-test-publishable-key" in data
    assert "paypal-client" in data

    # Negative test cases
    assert "stripe_secret_key" not in data
    assert "stripe_test_secret_key" not in data
