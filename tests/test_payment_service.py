import requests


def test_payment_authorise_and_capture():
    authorise_response = requests.post(
        "http://localhost:5003/payments/authorise",
        json={
            "card_token": "test-card",
            "amount": 120
        },
        timeout=5
    )

    assert authorise_response.status_code == 200

    authorisation = authorise_response.json()

    assert authorisation["status"] == "authorised"
    assert "authorisation_id" in authorisation

    capture_response = requests.post(
        "http://localhost:5003/payments/capture",
        json={
            "authorisation_id": authorisation["authorisation_id"]
        },
        timeout=5
    )

    assert capture_response.status_code == 200

    capture = capture_response.json()

    assert capture["status"] == "captured"
    assert "payment_id" in capture


def test_payment_declines_fail_card():
    response = requests.post(
        "http://localhost:5003/payments/authorise",
        json={
            "card_token": "fail-card",
            "amount": 120
        },
        timeout=5
    )

    assert response.status_code == 402

    data = response.json()

    assert data["status"] == "declined"