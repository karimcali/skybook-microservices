from flask import Flask, jsonify
import pika
import json
import os
import time
import threading

app = Flask(__name__)

tickets = {}

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
QUEUE_NAME = "ticket_booking_confirmed"


@app.get("/health")
def health():
    return jsonify({
        "service": "ticket-service",
        "status": "ok"
    })


@app.get("/tickets/<booking_id>")
def get_ticket(booking_id):
    ticket = tickets.get(booking_id)

    if not ticket:
        return jsonify({"error": "Ticket not found"}), 404

    return jsonify(ticket)


def handle_message(channel, method, properties, body):
    try:
        event = json.loads(body)

        booking_id = event.get("booking_id")

        if not booking_id:
            print("Event ignored because booking_id is missing")
            channel.basic_ack(delivery_tag=method.delivery_tag)
            return

        ticket = {
            "ticket_id": "TICKET-" + booking_id,
            "booking_id": booking_id,
            "flight_id": event.get("flight_id"),
            "seat": event.get("seat"),
            "passenger_name": event.get("passenger_name"),
            "status": "issued"
        }

        tickets[booking_id] = ticket

        print("Ticket created:", ticket)

        channel.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as error:
        print("Error handling ticket event:", error)
        channel.basic_ack(delivery_tag=method.delivery_tag)


def consume_events():
    while True:
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=RABBITMQ_HOST)
            )

            channel = connection.channel()
            channel.queue_declare(queue=QUEUE_NAME)

            channel.basic_consume(
                queue=QUEUE_NAME,
                on_message_callback=handle_message
            )

            print("ticket-service is waiting for booking events")
            channel.start_consuming()

        except Exception as error:
            print("Could not connect to RabbitMQ:", error)
            time.sleep(5)


if __name__ == "__main__":
    consumer_thread = threading.Thread(target=consume_events)
    consumer_thread.daemon = True
    consumer_thread.start()

    app.run(host="0.0.0.0", port=5004)