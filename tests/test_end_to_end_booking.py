import time

import requests


def find_available_seat():
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

    for flight in flights:
        seats = flight.get("seats", {})

        for seat, status in seats.items():
            if status == "available":
                return flight["flight_id"], seat

        available_seats = flight.get("available_seats", [])

        if available_seats:
            return flight["flight_id"], available_seats[0]

    raise AssertionError("No available seat found for test")


def test_full_booking_creates_ticket_and_notification():
    flight_id, seat = find_available_seat()

    booking_response = requests.post(
        "http://localhost:5001/bookings",
        json={
            "flight_id": flight_id,
            "seat": seat,
            "passenger_name": "Test Passenger",
            "card_token": "test-card"
        },
        timeout=8
    )

    assert booking_response.status_code == 201

    booking = booking_response.json()

    assert booking["flight_id"] == flight_id
    assert booking["seat"] == seat
    assert booking["status"] == "confirmed"
    assert "booking_id" in booking

    time.sleep(2)

    ticket_response = requests.get(
        f"http://localhost:5004/tickets/{booking['booking_id']}",
        timeout=5
    )

    assert ticket_response.status_code == 200

    ticket = ticket_response.json()

    assert ticket["booking_id"] == booking["booking_id"]
    assert ticket["status"] == "issued"

    notification_response = requests.get(
        f"http://localhost:5005/notifications/{booking['booking_id']}",
        timeout=5
    )

    assert notification_response.status_code == 200

    notification = notification_response.json()

    assert notification["booking_id"] == booking["booking_id"]
    assert notification["status"] == "sent"