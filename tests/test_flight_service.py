import requests


def test_flight_search_returns_flights():
    response = requests.get(
        "http://localhost:5002/flights",
        params={
            "origin": "Dublin",
            "destination": "London",
            "date": "2026-05-10"
        },
        timeout=5
    )

    assert response.status_code == 200

    flights = response.json()

    assert len(flights) > 0
    assert flights[0]["origin"] == "Dublin"
    assert flights[0]["destination"] == "London"
    assert flights[0]["date"] == "2026-05-10"


def test_holding_missing_seat_returns_400():
    response = requests.post(
        "http://localhost:5002/flights/FL100/hold-seat",
        json={},
        timeout=5
    )

    assert response.status_code == 400
    assert "error" in response.json()