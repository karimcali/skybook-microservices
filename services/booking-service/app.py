from flask import Flask, jsonify, request
from uuid import uuid4
import requests
import pika
import json

app = Flask(__name__)

FLIGHT_SERVICE_URL = "http://flight-service:5002"
PAYMENT_SERVICE_URL = "http://payment-service:5003"
RABBITMQ_HOST = "rabbitmq"

bookings = {}


@app.get("/health")
def health():
    return jsonify({
        "service": "booking-service",
        "status": "ok"
    })


@app.get("/bookings/<booking_id>")
def get_booking(booking_id):
    booking = bookings.get(booking_id)

    if not booking:
        return jsonify({"error": "Booking not found"}), 404

    return jsonify(booking)


@app.post("/bookings")
def create_booking():
    data = request.get_json() or {}

    flight_id = data.get("flight_id")
    seat = data.get("seat")
    passenger_name = data.get("passenger_name")
    card_token = data.get("card_token")

    if not flight_id:
        return jsonify({"error": "flight_id is required"}), 400

    if not seat:
        return jsonify({"error": "seat is required"}), 400

    if not passenger_name:
        return jsonify({"error": "passenger_name is required"}), 400

    if not card_token:
        return jsonify({"error": "card_token is required"}), 400

    seat_response = requests.post(
        f"{FLIGHT_SERVICE_URL}/flights/{flight_id}/hold-seat",
        json={"seat": seat},
        timeout=5
    )

    if seat_response.status_code != 200:
        return jsonify({
            "error": "Seat hold failed",
            "details": seat_response.json()
        }), seat_response.status_code

    price = seat_response.json().get("price", 120)

    authorise_response = requests.post(
        f"{PAYMENT_SERVICE_URL}/payments/authorise",
        json={
            "card_token": card_token,
            "amount": price
        },
        timeout=5
    )

    if authorise_response.status_code != 200:
        return jsonify({
            "error": "Payment authorisation failed",
            "details": authorise_response.json()
        }), authorise_response.status_code

    authorisation_id = authorise_response.json()["authorisation_id"]

    capture_response = requests.post(
        f"{PAYMENT_SERVICE_URL}/payments/capture",
        json={
            "authorisation_id": authorisation_id
        },
        timeout=5
    )

    if capture_response.status_code != 200:
        return jsonify({
            "error": "Payment capture failed",
            "details": capture_response.json()
        }), capture_response.status_code

    payment_id = capture_response.json()["payment_id"]
    booking_id = "BKG-" + str(uuid4())[:8]

    booking = {
        "booking_id": booking_id,
        "flight_id": flight_id,
        "seat": seat,
        "passenger_name": passenger_name,
        "payment_id": payment_id,
        "status": "confirmed"
    }

    bookings[booking_id] = booking

    publish_booking_confirmed(booking)

    return jsonify(booking), 201


def publish_booking_confirmed(booking):
    event = {
        "event_type": "booking_confirmed",
        "booking_id": booking["booking_id"],
        "flight_id": booking["flight_id"],
        "seat": booking["seat"],
        "passenger_name": booking["passenger_name"],
        "payment_id": booking["payment_id"],
        "status": "confirmed"
    }

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=RABBITMQ_HOST)
    )

    channel = connection.channel()

    queues = [
        "ticket_booking_confirmed",
        "notification_booking_confirmed"
    ]

    for queue in queues:
        channel.queue_declare(queue=queue)
        channel.basic_publish(
            exchange="",
            routing_key=queue,
            body=json.dumps(event)
        )

    connection.close()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)